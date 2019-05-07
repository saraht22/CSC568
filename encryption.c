#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>

//gcc encryption.c -o encryption
//./encryption argument1: old path, argument2: new path
int getfilesize(char *path)
{
    FILE *pf = fopen(path, "r");
    if (pf == NULL)
    {
        return -1;
    }
    else
    {
        fseek(pf, 0, SEEK_END);
        int length = ftell(pf);
        return length;
    }
}

void copy(char *oldpath, char *newpath)
{
    FILE *pfr, *pfw;
    pfr = fopen(oldpath, "rb");
    pfw = fopen(newpath, "wb");
    if (pfr == NULL || pfw == NULL)
    {
        fclose(pfr);
        fclose(pfw);
        return;
    }
    else
    {
        int length = getfilesize(oldpath);
        char *p = (char *)malloc(length*sizeof(char));
        fread(p, sizeof(char), length, pfr);
        fwrite(p, sizeof(char), length, pfw);
        fclose(pfr);
        fclose(pfw);
    }
}

void en(char *oldpath, char *newpath, int hash)
{
    FILE *pfr, *pfw;
    pfr = fopen(oldpath, "rb");
    pfw = fopen(newpath, "wb");
    if (pfr == NULL || pfw == NULL)
    {
        fclose(pfr);
        fclose(pfw);
        return;
    }
    else
    {
        int length = getfilesize(oldpath);
        char *p = (char *)malloc(length*sizeof(char));
        fread(p, sizeof(char), length, pfr);
        for (int i = 0; i < length; i++)
        {
            p[i] ^= hash;
        }
        fwrite(p, sizeof(char), length, pfw);
        fclose(pfr);
        fclose(pfw);
    }
}

int hash(const char *word) {
    int hash = 0;
    int n;
    for (int i = 0; word[i] != '\0'; i++) {
        // alphabet case
        if (isalpha(word[i]))
            n = word[i] - 'a' + 1;
        else  // comma case
            n = 27;

//        hash = ((hash << 3) + n) % SIZE;
        hash = ((hash << 3) + n);
    }
    return hash;
}

int main(int argc, char *argv[])
{
//    char *oldpath = "/Users/hongyifan/Downloads/lmbench-3.0-a9";
//    char *newpath = "/Users/hongyifan/Downloads/encrypted.zip";

    char *oldpath = argv[1];
    char *newpath = argv[2];

    //zip it to: /Users/hongyifan/Downloads/lmbench-3.0-a9.zip
    //zip -r /Users/hongyifan/Downloads/lmbench-3.0-a9.zip /Users/hongyifan/Downloads/lmbench-3.0-a9

    char zippath[1000];
    strcpy(zippath,oldpath);
    strcat(zippath,".zip");

    char s1[1000];
    strcpy(s1, "zip -r -q ");
    strcat(s1,zippath);
    strcat(s1," ");
    strcat(s1,oldpath);
    printf("%s\n",s1);
    system(s1);

    char password[50],password_conf[50];
    char *pwd=getpass("password:\n");
    strcpy(password, pwd);
    char *confirm=getpass("confirm password:\n");
    strcpy(password_conf, confirm);

    if(strcmp(password,password_conf)==0)
        printf("correct\n");
    else{
        printf("incorrect\n");
        return 0;
    }

//    printf("%d",hash(password));
    en(zippath, newpath,hash(password));

    return 0;
}
