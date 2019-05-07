#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>

//gcc decryption.c -o decryption
//./decryption

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

void de(char *oldpath, char *newpath, int hash)
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
//    char *newpath = "/Users/hongyifan/Downloads/encrypted.zip"; //same as newpath in encrypt program
//    char *newdepath = "/Users/hongyifan/Downloads/lmbench-3.0-a9-decrypted.zip";

    char *newpath = argv[1];
    char *newdepath = argv[2];

    char password[50];
    char *pwd=getpass("password:\n");
    strcpy(password, pwd);

    de(newpath, newdepath,hash(password));
    //unzip to: /Users/hongyifan/Downloads/lmbench-3.0-a9-decrypted
    //unzip /Users/hongyifan/Downloads/lmbench-3.0-a9-decrypted.zip
//    char s1[1000];
//    strcpy(s1, "unzip ");
//    strcat(s1,newdepath);
//    strcat(s1," -d ");
//    strcat(s1,"/Users/hongyifan/Downloads/lmbench-3.0-a9-decrypted");
//    printf("%s\n",s1);
//    system(s1);

    return 0;
}
