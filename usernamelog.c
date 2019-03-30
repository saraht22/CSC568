#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//gcc usernamelog.c -o usernamelog
//./usernamelog
int main(int argc, char *argv[]) {
    char username[100], date[100];
    FILE *fp1=popen("whoami","r");
    fscanf(fp1,"%s", username);
    pclose(fp1);

    FILE *fp2=popen("date","r");
    fscanf(fp2,"%[^\n]s", date);
    pclose(fp2);
    printf("%s\n",username);
    printf("%s\n",date);
    return 0;
}