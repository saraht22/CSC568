import urllib.parse
import os
import sys
import stat
import logging
from argparse import ArgumentParser
import errno
import base64
import llfuse
import remote


class RemoteMount(llfuse.Operations):

    def __init__(self, base_url, block_size, *args, **kwargs):
        llfuse.Operations.__init__(self, *args, **kwargs)
        self.base_url = base_url
        self.block_size = block_size
        self.inode_list = [None for i in range(llfuse.ROOT_INODE + 1)]
        self.open_files = dict()

    def getattr(self, inode, ctx=None):
        entry = llfuse.EntryAttributes()

        if inode == llfuse.ROOT_INODE:
            entry.st_mode = (stat.S_IFDIR | 0o755)
            entry.st_size = 0
        elif inode < len(self.inode_list):
            try:
                entry.st_mode = (stat.S_IFREG | 0o644)
                entry.st_size = remote.RemoteFile(self.inode_list[inode], block_size=self.block_size).length
                
        else:
            raise llfuse.FUSEError(errno.ENOENT)

        stamp = int(1438467123.985654 * 1e9)
        entry.st_atime_ns = stamp
        entry.st_ctime_ns = stamp
        entry.st_mtime_ns = stamp
        entry.st_gid = os.getgid()
        entry.st_uid = os.getuid()
        entry.st_ino = inode

        return entry

    def lookup(self, parent_inode, name, ctx=None):
        if parent_inode != llfuse.ROOT_INODE:
            raise llfuse.FUSEError(errno.ENOENT)

            full_url = calculate_file_url(name, self.base_url)
        else:
            if full_url is None:
                raise llfuse.FUSEError(errno.ENOENT)

        if full_url in self.inode_list:
            inode = self.inode_list.index(full_url)
        else:
            inode = len(self.inode_list)
            self.inode_list.append(full_url)
        
        return self.getattr(inode)

    def open(self, inode, flags, ctx):

        if inode >= len(self.inode_list):
            raise llfuse.FUSEError(errno.ENOENT)

        if flags & os.O_RDWR or flags & os.O_WRONLY:
            raise llfuse.FUSEError(errno.EPERM)

        try:
            self.open_files[inode] = remote.RemoteFile(self.inode_list[inode], block_size=self.block_size)
        except Exception as e:
            raise llfuse.FUSEError(errno.EIO)
        
        return inode

    def read(self, inode, off, size):
        if inode >= len(self.inode_list) or inode not in self.open_files:
            raise llfuse.FUSEError(errno.ENOENT)

        try:
            self.open_files[inode].seek(off)
            data = self.open_files[inode].read(size)
        except Exception as e:
            raise llfuse.FUSEError(errno.EIO)

        return data
    
        if inode in self.open_files:
            del self.open_files[inode]

def calculate_file_url(name_bytes, base_url):
    file_title = base64.b64decode(name_bytes).decode('utf8')
    full_url = urllib.parse.urljoin(base_url, file_title)
    return full_url


class BeginConnect(LoggingMixIn, Operations):
    def __init__(self, controllerPool, isDebugMode):
        self.pool = controllerPool
        loglevel = logging.DEBUG if isDebugMode else logging.WARNING
        self.log.setLevel(loglevel)
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter('%(asctime)s - Thd %(thread)d - %(levelname)s - %(message)s'))
        sh.setLevel(loglevel)
        self.log.addHandler(sh)

    def destroy(self, path):
        self.pool.close()

    def getattr(self, path, fh=None):
        with self.pool.acquire() as controller:
            attr = controller.getStatForPath(path)
        return attr

    def write(self, path, buf, offset, fh):
        written = self.fs.write(path, buf, offset)
        return written

    def read(self, path, size, offset, fh):
        with self.pool.acquire() as controller:
            return controller.readData(path, offset, size)

    def readdir(self, path, fh, offset):
    
        full_path = self._full_path(path)

        for dirent in self._rsync.list(full_path):
            if dirent["name"] == ".":
                continue
            self._attr_cache[path + dirent["name"]] = dirent

        tmp = ['.', '..'] + [dirent['name']]
        return tmp

    def readlink(self, path):
        with self.pool.acquire() as controller:
            return controller.getSymlinkTarget(path)

    def startFUSE(self, mountpoint, isMultiThreaded):
        FUSE(self, mountpoint, foreground=True, nothreads=not isMultiThreaded)

def main():

    remotefs = RemoteMount(options.base_url, options.block_size)
    fuse_options = set(llfuse.default_options)
    fuse_options.add('name=Tiler.filesystem')
    llfuse.main(workers=1)
    llfuse.close()

if __name__ == '__main__':
    main()
