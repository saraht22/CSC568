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

/* Encrypt the files
*/
static int worm_encryption(const char *path, struct key, 


/* Deduplication
*/
static int master_comparesize()
{
}

static int master_comparehash()
{
}


static int master_encryption()
{
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
			   
			   
char* root_path;
char* password;

/* is_encrypted: returns 1 if encryption succeeded, 0 otherwise */
int is_encrypted(const char *path)
{
	int ret;
	char xattr_val[5];
	getxattr(path, "user.encfs", xattr_val, sizeof(char)*5);
	fprintf(stderr, "xattr set to: %s\n", xattr_val);

	ret = (strcmp(xattr_val, "true") == 0);
	return ret;
}

/* add_encrypted_attr: returns 1 on success, 0 on failure */
int add_encrypted_attr(const char *path)
{
	int ret;
	int setxattr_ret;
	setxattr_ret = setxattr(path, "user.encfs", "true", (sizeof(char)*5), 0);
	ret = setxattr_ret == 0;
	fprintf(stderr, "\nsetxattr %s\n", ret > 0 ? "succeeded" : "failed");
	return ret;
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

static int xmp_access(const char *fuse_path, int mask)
{
	char *path = prefix_path(fuse_path);

	int res;

	res = access(path, mask);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_readlink(const char *fuse_path, char *buf, size_t size)
{
	char *path = prefix_path(fuse_path);

	int res;

	res = readlink(path, buf, size - 1);
	if (res == -1)
		return -errno;

	buf[res] = '\0';
	return 0;
}

static int xmp_readdir(const char *fuse_path, void *buf, fuse_fill_dir_t filler,
		       off_t offset, struct fuse_file_info *fi)
{
	char *path = prefix_path(fuse_path);

	DIR *dp;
	struct dirent *de;
	fprintf(stderr, "Path: %s\n", path);

	(void) offset;
	(void) fi;

	dp = opendir(path);
	if (dp == NULL)
		return -errno;

	while ((de = readdir(dp)) != NULL) {
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



