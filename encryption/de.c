int main(int argc, char *argv[]) {
    system("mkdir d3");
    system("encfs ~/Desktop/secondtest/mount/d1 ~/Desktop/secondtest/d3");
    system("cp ~/Desktop/secondtest/d3/target.zip ~/Desktop/secondtest");
    system("fusermount -u d3");
    system("fusermount -u mount");
    system("rm -rf ~/Desktop/secondtest/d3");
    system("./zipfs target.zip mount");
    system("rm target.zip");
    return 0;
}
/*
encfs ~/Desktop/secondtest/mount/d1 ~/Desktop/secondtest/d3
cp ~/Desktop/secondtest/d3/target.zip ~/Desktop/secondtest
fusermount -u d3
rm -rf ~/Desktop/secondtest/mount/d3
fusermount -u mount
./zipfs target.zip mount
*/
