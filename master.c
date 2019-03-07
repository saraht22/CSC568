#define FUSE_USE_VERSION 28
#define HAVE_SETXATTR
#define ENCRYPT 1
#define DECRYPT 0
#define PASS_THROUGH (-1)

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#ifdef linux
/* For pread()/pwrite() */
#define _XOPEN_SOURCE 500
#endif

#include <assert.h>
#include <fuse.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <linux/limits.h>
#include <fcntl.h>
#include <dirent.h>
#include <errno.h>
#include <sys/time.h>
#include "lib/aes-crypt.h"
#ifdef HAVE_SETXATTR
#include <sys/xattr.h>
#endif



char* root_path;
char* password;

/*
 * List the supported extended attributes.
 */
static int worm_listxattr(const char *path, char *list, size_t size)
{
	int res;
	char *ipath;
	
	ipath=translate_path(path);
	res = llistxattr(ipath, list, size);
   	free(ipath);
    if(res == -1) {
        return -errno;
    }
    return res;

}

/*
 * Get the value of an extended attribute.
 */
static int worm_getxattr(const char *path, const char *name, char *value, size_t size)
{
    int res;
    char *ipath;
    
    ipath=translate_path(path);
    res = lgetxattr(ipath, name, value, size);
    free(ipath);
    if(res == -1) {
        return -errno;
    }
    return res;
}

/* Encrypt the files
*/
static int worm_encryption(const char *path, struct key)
{
	int ret;
	char xattr_val[5];
	getxattr(path, "user.encfs", xattr_val, sizeof(char)*5);
	fprintf(stderr, "xattr set to: %s\n", xattr_val);

	ret = (strcmp(xattr_val, "true") == 0);
	return ret;
}

int add_encrypted_attr(const char *path)
{
	int ret;
	int setxattr_ret;
	setxattr_ret = setxattr(path, "user.encfs", "true", (sizeof(char)*5), 0);
	ret = setxattr_ret == 0;
	fprintf(stderr, "\nsetxattr %s\n", ret > 0 ? "succeeded" : "failed");
	return ret;
}


/* Deduplication
*/
static int master_comparesize(const int *filesize)
{
	tmp = filesize
	if(filesize == tmp) {
        return 1;
    } 
}

static int master_comparehash()
{
}
			   
char *prefix_path(const char *path)
{
	size_t len = strlen(path) + strlen(root_path) + 1;
	char *root_dir = malloc(len * sizeof(char));

	strcpy(root_dir, root_path);
	strcat(root_dir, path);

	return root_dir;
}

static int xmp_getattr(const char *fuse_path, struct stat *stbuf)
{
	char *path = prefix_path(fuse_path);

	int res;

	res = lstat(path, stbuf);
	if (res == -1)
		return -errno;

	return 0;
}

static int access(const char *fuse_path, int mask)
{
	char *path = prefix_path(fuse_path);

	int res;

	res = access(path, mask);
	if (res == -1)
		return -errno;

	return 0;
}

static int readlink(const char *fuse_path, char *buf, size_t size)
{
	char *path = prefix_path(fuse_path);

	int res;

	res = readlink(path, buf, size - 1);
	if (res == -1)
		return -errno;

	buf[res] = '\0';
	return 0;
}

static int master_permission()
{
}

static int master_addattri()
{
}

static int master_addfile()
{
}




