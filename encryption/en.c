int main(int argc, char *argv[]) {
    system("mkdir d1");
    system("mkdir d2");
    system("encfs ~/Desktop/secondtest/d1 ~/Desktop/secondtest/d2");
    system("cp target.zip ~/Desktop/secondtest/d2");
    system("fusermount -u d2");
    system("rm -rf ~/Desktop/secondtest/d2");
    system("rm target.zip");
    system("zip -r target.zip d1");
    system("rm -rf ~/Desktop/secondtest/d1");
    system("mkdir mount");
    system("./zipfs target.zip mount");
    system("rm target.zip");
    return 0;
}
/*
mkdir d1
mkdir d2
encfs ~/Desktop/secondtest/d1 ~/Desktop/secondtest/d2
cp target.zip ~/Desktop/secondtest/d2
fusermount -u d2
rm -rf ~/Desktop/secondtest/d2

rm target.zip
zip -r target.zip d1
rm -rf ~/Desktop/secondtest/d1
mkdir mount
./zipfs target.zip mount
*/
