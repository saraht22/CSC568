import os


class File:
    def __init__(self, path, name):
        self.name = name
        self.path = path
        self.size = None

    def getPath(self):
        return os.sep.join(self.path.getPath(), self.name)


class Path:
    def __init__(self, parent, name):
        self.name = name
        self.parent = parent
        self.entries = {}

    def getPath(self):
        if self.parent is None:
            return self.name
        else:
            return os.path.join(self.parent.getPath(), self.name)

    def add_entry(self, new_entry):
        self.entries[new_entry.name] = new_entry

    def find(self, name):
        return self.entries.get(name, None)


def getStatus(path):
    total_size = 0
    total_files = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
        total_files += len(filenames)
    return total_files, total_size


def splitPath(getPath):
    directories = []
    path = getPath
    print("path {}".format(path))

    while True:
        path, folder = os.path.split(path)

        if folder == '':
            if path != "":
                directories.append(path)
            break
        else:
            directories.append(folder)

    directories.reverse()
    return directories


class Cache:
    def __init__(self, config, backend):
        self.backend = backend
        self.path = path
        self.files, self.size = getStatus(self.path)
        self.root = Path(None, 'root')
        self.saveInfo()
        path = os.path.expanduser()

    def status(self):
        self.update_stats()
        s = {'size': self.size,
             'files': self.files}
        return s

    def saveInfo(self):
        infos = self.backend.ls('.', recursive=True)
        for info in infos:
            path = splitPath(info['name'])

            if info['type'] == 'dir':
                path = self.path
                for dirname in path:
                    temp = path.find(dirname)
                    if temp is None:
                        temp = Path(path, dirname)
                        path.add_entry(temp)
                        parent = temp
                temp2 = temp.find(path[-1])
                if temp2 is None:
                    temp2 = File(temp, path[-1])
                    temp.add_entry(temp2)
            
            elif info['type'] == 'file':
                root = self.root
                parent = self.root
                for dirname in path[:-1]:
                    root = root.find(dirname)
                    if temp is None:
                        temp = Path(root, dirname)
                        root.add_entry(temp)
                
        

