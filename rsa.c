#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>

//https://en.wikipedia.org/wiki/RSA_(cryptosystem)

//m^e mod n
int modpow(long long m, long long e, long long n) {
    int res = 1;
    res=pow(m,e);
    res%=n;
    return res;
}

// Encode: c = m^e mod n
int encode(int m, int e, int n) {
    return modpow(m, e, n);
}

//Decode: m = c^d mod n
int decode(int c, int d, int n) {
    return modpow(c, d, n);
}

//least common multiple
int lcm(int a, int b){
    int max, step, res=0;
    if(a > b)
        max = step = a;
    else
        max = step = b;

    while(1) {
        if(max%a == 0 && max%b == 0) {
            res = max;
            break;
        }

        max += step;
    }
    return res;
}


//modular multiplicative inverse with https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
//n^-1 mod m by extended euclidian method
int inverse(int n, int modulus) {
    int a = n, b = modulus;
    int x = 0, y = 1, x0 = 1, y0 = 0, q, temp;
    while(b != 0) {
        q = a / b;
        temp = a % b;
        a = b;
        b = temp;
        temp = x; x = x0 - q * x; x0 = temp;
        temp = y; y = y0 - q * y; y0 = temp;
    }
    if(x0 < 0) x0 += modulus;
    return x0;
}

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



//encode the file
//void encodeFile(){
//    encode(m,e,n);
//}

//decode the file
//void decodeFile(){
//    decode(c,d,n);
//}

int main(void) {
    int p=61, q=53, n, phi, lambda, e=17, d, bytes, len;
    int *encoded, *decoded;
    char *buffer;
    FILE *f, *fc;
    while(1) {
        printf("p = %d \n", p);
        printf("q = %d \n", q);
        n = p * q;
        printf("n = pq = %d \n", n);
        if(n < 128) {
            printf("Mod less than 128. Try again \n");
        }
        else break;
    }
    if(n >> 21) bytes = 3;
    else if(n >> 14) bytes = 2;
    else bytes = 1;
    phi = (p - 1) * (q - 1);
    lambda=lcm(p-1,q-1);
    printf("phi = %d, lambda= %d \n", phi, lambda);
    printf("e = %d\npublic key is (n=%d, e=%d) \n", e, n, e);
    d = inverse(e, lambda);
    printf("private exponent d = %d\nprivate key is (n=%d, d=%d) \n", d, n, d);
    printf("opening file \n");
    f = fopen("/Users/hongyifan/Downloads/HW8Solutions.pdf", "rb");
    //readfile
    fclose(f);
    fc = fopen("/Users/hongyifan/Downloads/encrypted.pdf","wb");
    //writefile
    fclose(fc);

    return 0;
}