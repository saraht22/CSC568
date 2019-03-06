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



