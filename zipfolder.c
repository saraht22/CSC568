#include <stdio.h>
#include <stdlib.h>
#include <string.h>
// gcc zipfolder.c -o zipfolder
// ./zipfolder argument1: name of zip file, argument2: path of folder
int main(int argc, char *argv[]) {
    char s1[100];
    strcpy(s1, "zip -r ");
    strcat(s1,argv[1]);
    strcat(s1," ");
    strcat(s1,argv[2]);
    printf("%s\n",s1);
    system(s1);
    return 0;
}