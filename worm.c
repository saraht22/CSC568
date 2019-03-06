#define FUSE_USE_VERSION 26

static const char* wormfsVersion = "2019.02.20";

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <stdio.h>
#include <strings.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/xattr.h>
#include <dirent.h>
#include <unistd.h>
#include <fuse.h>


// Global to store our read-write path
char *rw_path;

// Translate an wormfs path into it's underlying filesystem path

static char* translate_path(const char* path)
{

    char *rPath= malloc(sizeof(char)*(strlen(path)+strlen(rw_path)+1));
 
    strcpy(rPath,rw_path);
    if (rPath[strlen(rPath)-1]=='/') {
        rPath[strlen(rPath)-1]='\0';
    }
    strcat(rPath,path);

    return rPath;
}


static int worm_getattr(const char *path, struct stat *st_data)
{
    int res;
	char * ipath;
	ipath=translate_path(path);
	
    res = lstat(ipath, st_data);
    free(ipath);
    if(res == -1) {
        return -errno;
    }
    return 0;
}

static int worm_readlink(const char *path, char *buf, size_t size)
{
   	int res;
	char *ipath;
	ipath=translate_path(path);
	
    res = readlink(ipath, buf, size - 1);
    free(ipath);
    if(res == -1) {
        return -errno;
    }
    buf[res] = '\0';
    return 0;
}

static int worm_readdir(const char *path, void *buf, fuse_fill_dir_t filler,off_t offset, struct fuse_file_info *fi)
{
    DIR *dp;
    struct dirent *de;
    int res;

    (void) offset;
    (void) fi;
    char *ipath;

    ipath=translate_path(path);

    dp = opendir(ipath);
    free(ipath);
    if(dp == NULL) {
        res = -errno;
        return res;
    }

    while((de = readdir(dp)) != NULL) {
        struct stat st;
        memset(&st, 0, sizeof(st));
        st.st_ino = de->d_ino;
        st.st_mode = de->d_type << 12;
        if (filler(buf, de->d_name, &st, 0))
            break;
    }

    closedir(dp);
    return 0;
}

static int worm_open(const char *path, struct fuse_file_info *finfo)
{
	int res;
	
	/* We allow opens, unless they're tring to write, sneaky
	 * people.
	 */
	int flags = finfo->flags;
	
	if ((flags & O_WRONLY) || (flags & O_RDWR) || (flags & O_CREAT) || (flags & O_EXCL) || (flags & O_TRUNC) || (flags & O_APPEND)) {
      return -EROFS;
  	}
        char *ipath;	
  	ipath=translate_path(path);
  
    res = open(ipath, flags);
 
    free(ipath);
    if(res == -1) {
        return -errno;
    }
    close(res);
    return 0;
}

static int worm_read(const char *path, char *buf, size_t size, off_t offset, struct fuse_file_info *finfo)
{
    int fd;
    int res;
    (void)finfo;
    char *ipath;

    ipath=translate_path(path);
    fd = open(ipath, O_RDONLY);
    free(ipath);
    if(fd == -1) {
        res = -errno;
        return res;
    } 
    res = pread(fd, buf, size, offset);
    
    if(res == -1) {
        res = -errno;
	}
    close(fd);
    return res;
}

static int worm_statfs(const char *path, struct statvfs *st_buf)
{
  int res;	
  char *ipath;
  ipath=translate_path(path);
  
  res = statvfs(path, st_buf);
  free(ipath);
  if (res == -1) {
    return -errno;
  }
  return 0;
}




static int worm_access(const char *path, int mode)
{
	int res;
	char *ipath;
  	ipath=translate_path(path);
  	
  	/* Don't pretend that we allow writing
  	 * Chris AtLee <chris@atlee.ca>
  	 */
    if (mode & W_OK)
        return -EROFS;
        
  	res = access(ipath, mode);
	free(ipath);
  	if (res == -1) {
    	return -errno;
  	}
  	return res;
}






static int worm_mknod(const char *path, mode_t mode, dev_t rdev)
{
  (void)path;
  (void)mode;
  (void)rdev;
  return -EROFS;
}

static int worm_mkdir(const char *path, mode_t mode)
{
  (void)path;
  (void)mode;
  return -EROFS;
}

static int worm_unlink(const char *path)
{
  (void)path;
  return -EROFS;
}

static int worm_rmdir(const char *path)
{
  (void)path;
  return -EROFS;
}

static int worm_symlink(const char *from, const char *to)
{
  (void)from;
  (void)to;
  return -EROFS;	
}

static int worm_rename(const char *from, const char *to)
{
  (void)from;
  (void)to;
  return -EROFS;
}

static int worm_link(const char *from, const char *to)
{
  (void)from;
  (void)to;
  return -EROFS;
}

static int worm_chmod(const char *path, mode_t mode)
{
  (void)path;
  (void)mode;
  return -EROFS;
    
}

static int worm_chown(const char *path, uid_t uid, gid_t gid)
{
  (void)path;
  (void)uid;
  (void)gid;
  return -EROFS;
}

static int worm_truncate(const char *path, off_t size)
{
	(void)path;
  	(void)size;
  	return -EROFS;
}

static int worm_utime(const char *path, struct utimbuf *buf)
{
	(void)path;
  	(void)buf;
  	return -EROFS;	
}


static int worm_write(const char *path, const char *buf, size_t size, off_t offset, struct fuse_file_info *finfo)
{
  (void)path;
  (void)buf;
  (void)size;
  (void)offset;
  (void)finfo;
  return -EROFS;
}


static int worm_release(const char *path, struct fuse_file_info *finfo)
{
  (void) path;
  (void) finfo;
  return 0;
}

static int worm_fsync(const char *path, int crap, struct fuse_file_info *finfo)
{
  (void) path;
  (void) crap;
  (void) finfo;
  return 0;
}


static int worm_setxattr(const char *path, const char *name, const char *value, size_t size, int flags)
{
	(void)path;
	(void)name;
	(void)value;
	(void)size;
	(void)flags;
	return -EROFS;
}

static int worm_removexattr(const char *path, const char *name, const char *value, size_t size, int flags)
{
	(void)path;
	(void)name;
	(void)value;
	(void)size;
	(void)flags;
	return -EROFS;
}



struct fuse_operations worm_oper = {
    .getattr	= worm_getattr,
    .readlink	= worm_readlink,
    .readdir	= worm_readdir,
    .mknod		= worm_mknod,
    .mkdir		= worm_mkdir,
    .symlink	= worm_symlink,
    .unlink		= worm_unlink,
    .rmdir		= worm_rmdir,
    .rename		= worm_rename,
    .link		= worm_link,
    .chmod		= worm_chmod,
    .chown		= worm_chown,
    .truncate	= worm_truncate,
    .utime		= worm_utime,
    .open		= worm_open,
    .read		= worm_read,
    .write		= worm_write,
    .statfs		= worm_statfs,
    .release	= worm_release,
    .fsync		= worm_fsync,
    .access		= worm_access,

    /* Extended attributes support for userland interaction */
    .setxattr	= worm_setxattr,
    .removexattr= worm_removexattr
};

enum {
    KEY_HELP,
    KEY_VERSION,
};

static void usage(const char* progname)
{
    fprintf(stdout,
"usage: %s readwritepath mountpoint [options]\n"
"\n"
"   Mounts readwritepath as a read-only mount at mountpoint\n"
"\n"
"general options:\n"
"   -o opt,[opt...]     mount options\n"
"   -h  --help          print help\n"
"   -V  --version       print version\n"
"\n", progname);
}

static int wormfs_parse_opt(void *data, const char *arg, int key,
        struct fuse_args *outargs)
{
    (void) data;

    switch (key)
    {
        case FUSE_OPT_KEY_NONOPT:
            if (rw_path == 0)
            {
                rw_path = strdup(arg);
                return 0;
            }
            else
            {
                return 1;
            }
        case FUSE_OPT_KEY_OPT:
            return 1;
        case KEY_HELP:
            usage(outargs->argv[0]);
            exit(0);
        case KEY_VERSION:
            fprintf(stdout, "wormfs version %s\n", wormfsVersion);
            exit(0);
        default:
            fprintf(stderr, "see `%s -h' for usage\n", outargs->argv[0]);
            exit(1);
    }
    return 1;
}

static struct fuse_opt wormfs_opts[] = {
    FUSE_OPT_KEY("-h",          KEY_HELP),
    FUSE_OPT_KEY("--help",      KEY_HELP),
    FUSE_OPT_KEY("-V",          KEY_VERSION),
    FUSE_OPT_KEY("--version",   KEY_VERSION),
    FUSE_OPT_END
};


int main(int argc, char *argv[])
{
    struct fuse_args args = FUSE_ARGS_INIT(argc, argv);
    int res;

    res = fuse_opt_parse(&args, &rw_path, wormfs_opts, wormfs_parse_opt);
    if (res != 0)
    {
        fprintf(stderr, "Invalid arguments\n");
        fprintf(stderr, "see `%s -h' for usage\n", argv[0]);
        exit(1);
    }
    if (rw_path == 0)
    {
        fprintf(stderr, "Missing readwritepath\n");
        fprintf(stderr, "see `%s -h' for usage\n", argv[0]);
        exit(1);
    }

    #if FUSE_VERSION >= 26
        fuse_main(args.argc, args.argv, &worm_oper, NULL);
    #else
        fuse_main(args.argc, args.argv, &worm_oper);
    #endif

    return 0;
}

