from errno import ENOENT
from os.path import normpath
from paramiko import SSHClient, WarningPolicy
from urllib.parse import urlsplit
from os import SEEK_SET, SEEK_CUR, SEEK_END
from contextlib import contextmanager
from os import getgid, getuid
import os.path
import stat
from threading import Semaphore
BLOCK_SIZE = (1024*8)

class MountSource:
    def __init__(self, source_link):
        components = urlsplit(source_link)
        hostname = components.hostname
        if components.username is None:
            username = 'anonymous' 
        else:
            username = components.username
        port = 1111 if components.port is None else components.port
       
        remote_object = normpath(remote_object)
        self.remote_object = remote_object
        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(WarningPolicy())
        self.client.connect(hostname=hostname, port=port, username=username, compress=True)

        self.sftp = self.client.open_sftp()

        self.lofFP = None
        self.lofPath = None

    def close(self):
        if self.lofFP is not None:
            del self.lofFP
        self.sftp.close()
        self.client.close()

    def getRemoteEntries(self, path):
        return self.sftp.listdir_attr(self.remote_object + path)

    def getTargetLink(self, path):
        return self.sftp.readlink(self.remote_object + path)

    def getRemoteFolders(self):
        return self.remote_object

    def read(self, path, offset, size, count):
        out = BytesIO()
        ff = self.getdata(path)
		
        if self.lofPath != path:
            if self.lofFP is not None:
                self.lofFP.close()
            self.lofFP = self.sftp.open(self.remote_object + path, 'r')
            self.lofPath = path
        datachunks = self.lofFP.readv([(offset, size)])
        if count is None:
            count = self.length - self.offset
        
        while count:
            chunk_offset = (self.offset // self.block_size) * self.block_size
            if chunk_offset not in self.chunks:
                range = chunk_offset, min(self.length, self.offset + self.block_size) - 1
                self.chunks[chunk_offset] = BytesIO(self.getRange(*range))
            
            chunk = self.chunks[chunk_offset]
            chunk_offset = self.offset % self.block_size
            chunk_count = min(count, self.block_size - chunk_offset)
            chunk.seek(chunk_offset, SEEK_SET)
            out.write(chunk.read(chunk_count))
            
            count -= chunk_count
            self.offset += chunk_count

        out.seek(0)
        return ff[offset:offset + size] + out.read()
        

    
    def downloadData(self, pathDic, offset, size):
        path = pathDic['directory'] + pathDic['name']
        data = self.source.readData(path, offset, size)
        self.target.writeData(path, offset, data)
        path = pathDic['path']
        self.metadata.begin()
        self.metadata.removeRemoteSegments(path, offset, offset + size - 1)

        if len(self.metadata.getRemoteSegments(path)) == 0:
            self.metadata.setPathSynced(path)
        self.metadata.commit()

        return data

class MountLoadTarget:
    def __init__(self, targetDirectory):
        self.targetDirectory = abspath(targetDirectory)
        self.metaDirectory = self.targetDirectory + '/.mountload'

    def read(self, relativePath, offset, size):
        f = open(self.findPath(relativePath), 'rb')
        f.seek(offset, os.SEEK_SET)
        data = f.read(size)
        f.close()
        return data

    def write(self, relativePath, offset, data, mode):
        path = self.findPath(relativePath)
        f = open(path, 'w+')
        os.chmod(path, mode)
        f.seek(offset, os.SEEK_SET)
        f.write(data)
        f.close()
        return data

    def createDirectory(self, relativePath, mode):
        dirpath = self.findPath(relativePath)
        if isdir(dirpath):
            os.chmod(dirpath, mode)
        else:
            os.mkdir(dirpath, mode)


    def createSymlink(self, relativePath, target):
        os.symlink(target, self.findPath(relativePath))


    def getSymlink(self, relativePath):
        return os.readlink(self.findPath(relativePath))

    def findPath(self, relativePath):
        realPath = self.targetDirectory + relativePath
        if realPath.startswith(self.metaDirectory + '/'):
            realPath = relativePath
        return realPath


class RemoteFile:
    def __init__(self, url, verbose=False, BLOCK_SIZE=(1024*8)):
        self.verbose = verbose
        self.url = url
        self.length = self.getTotalLength()
        self.chunks = {}
        self.offset = 0
        self.block_size = BLOCK_SIZE

    def getTotalLength(self):
        
        resp = requests.head(self.url)
        length = int(resp.headers['content'])
        return length

    def getRange(self, start, end):
        headers = {'Range': 'bytes={}-{}'.format(start, end)}
        resp = requests.get(self.url, headers=headers)
        return resp.content

    def open(self, path, flags):

        full_path = self._full_path(path)
        with self._file_cache_lock:
            if not path in self._file_cache:
                localfile = self._rsync.copy(full_path)
                self._file_cache[path] = {"refcount": 1, "localpath": localfile}
            else:
                self._file_cache[path]["refcount"] += 1
                localfile = self._file_cache[path]["localpath"]

        handle = os.open(localfile, os.O_RDONLY)

    def read(self, count=None):
        if count is None:
            count = self.length - self.offset

        out = BytesIO()
        if count is not None:
            out.seek(0)
        return out.read()

    def seek(self, offset, whence=SEEK_SET):
        if whence == SEEK_SET:
            self.offset = offset
        elif whence == SEEK_END:
            self.offset = self.length + offset
        elif whence == SEEK_CUR:
            self.offset += offset

    def getOffset(self):
        return self.offset