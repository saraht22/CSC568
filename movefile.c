#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
//gcc movefile.c -o movefile
//./movefile file folder

int main(int argc, char *argv[]){
    char *file=argv[1];
    char *folder=argv[2];

    char s1[1000];
    strcpy(s1, "mv ");
    strcat(s1,file);
    strcat(s1," ");
    strcat(s1,folder);
    system(s1);

    return 0;
}