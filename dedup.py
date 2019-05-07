import os
from os import walk
from hashlib import sha1 as Hasher
from datetime import datetime
from optparse import OptionParser


def usage():
    usage = 'usage: python dedup.py folder_for_dedup'
    parser = OptionParser(usage)
    global folders
    (options, folders) = parser.parse_args()
    if len(folders) < 1:
        parser.print_help()
        exit(0)


def getfiles():
    files_size = 0
    device = None
    visited_inodes = set()
    for folder in folders:
        for root, dirs, files_ in walk(folder):
            for name in files_:
                filename = os.path.join(root, name)
                filesize = os.path.getsize(filename)
                if filesize is None:
                    continue
                stat = os.stat(filename)
                if device is None:
                    device = stat.st_dev
                else:
                    if device != stat.st_dev:
                        continue
                linked_files = 0
                linked_bytes = 0
                if stat.st_ino in visited_inodes:
                    linked_bytes += filesize
                visited_inodes.add(stat.st_ino)
                files_size += filesize
                yield '%s%s%s' % (filesize, '\0', filename)


def file_hash(filename):
    buffer_size = 64 * 1024
    f = open(filename, "rb")
    hasher = Hasher()
    size_read = 0
    chunk = True
    while chunk:
        chunk = f.read(buffer_size)
        size_read += len(chunk)
        hasher.update(chunk)
    f.close()
    return hasher.hexdigest()


def dedup(fin, fout, tmp_path):
    def match(group, group_number, sid):
        if len(group) > 1:
            d = {}
            for s in group:
                d.setdefault(file_hash(s), []).append(s)
            for k, v in d.items():
                if len(v) > 1:
                    sout.write(''.join('%s-%s%s%s\n' % (sid, k, '\0', s) for s in v))

    with open('%s.%s' % (tmp_path, fout), 'w') as sout:
        with open('%s.%s.sorted' % (tmp_path, fin)) as files:
            old = None
            group = []
            group_number = 1
            sid = None
            for line in files:
                line = line.strip()
                sid, filename = line.split('\0')
                if old and sid != old:
                    match(group, group_number, sid)
                    group = []
                    group_number += 1
                group.append(filename)
                old = sid
            if group:
                match(group, group_number, sid)
    os.system('sort -n %s.%s > %s.%s.sorted' % (tmp_path, fout, tmp_path, fout))
    os.unlink('%s.%s.sorted' % (tmp_path, fin))
    os.unlink('%s.%s' % (tmp_path, fout))


def main():
    usage()
    tmp_path = '/tmp/dup-' + Hasher(str(datetime.now()).encode()).hexdigest()[:6]
    # read files
    with open('%s.sizes' % tmp_path, 'w') as tmpfiles:
        for f in getfiles():
            tmpfiles.write(f + '\n')

    os.system('sort %s.sizes > %s.sizes.sorted' % (tmp_path, tmp_path))
    os.unlink('%s.sizes' % tmp_path)

    dedup('sizes', 'fullhash', tmp_path)

    with open('%s.%s.sorted' % (tmp_path, 'fullhash')) as files:
        old = None
        group = []
        group_number = 1
        for line in files:
            line = line.strip()
            sid, filename = line.split('\0')
            if old and sid != old:
                for f in group[1:]:
                    tmp = f + '~D~'
                    os.rename(f, tmp)
                    os.link(group[0], f)
                    os.unlink(tmp)
                group = []
                group_number += 1
            group.append(filename)
            old = sid
        if group:
            for f in group[1:]:
                tmp = f + '~D~'
                os.rename(f, tmp)
                os.link(group[0], f)
                os.unlink(tmp)
    os.unlink('%s.fullhash.sorted' % tmp_path)


if __name__ == "__main__":
    main()
