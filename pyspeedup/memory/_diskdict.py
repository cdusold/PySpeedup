from collections import MutableMapping
import pickle
from os.path import expanduser,join
from os import remove,makedirs
from glob import glob
import atexit

def _exitgracefully(self):
    '''
    Save all the values to disk before closing.
    '''
    if self is None or not hasattr(self,"_save_page_to_disk"):
        return
    while len(self.pages)>0:
        for key in list(self.pages.keys()):
            self._save_page_to_disk(key)
class _page(dict):
    currentDepth=0
class DiskDict(MutableMapping):
    """
    A dictionary class that maintains O(1) look up and write while keeping RAM usage O(1) as well.

    This is accomplished through a rudimentary (for now) hashing scheme to page the
    dictionary into parts.

    The object created can be used any way a normal dict would be used, and will
    clean itself up on python closing. This means saving all the remaining pages
    to disk. If the file_basename and file_location was used before, it will load
    the old values back into itself so that the results can be reused.

    There are two ways to initialize this object, as a standard object:

        >>> diskDict = DiskDict("sample")
        >>> for i in range(10):
        ...     diskDict[i] = chr(97+i)
        ...
        >>> diskDict[3]
        'd'
        >>> del diskDict[5]
        >>> ", ".join(str(x) for x in diskDict.keys())
        0, 1, 2, 3, 4, 6, 7, 8, 9
        >>> "b" in diskDict
        True

    Or through context:

        >>> with DiskDict("test") as d:
        ...     for i in range(10):
        ...         d[i] = chr(97+i)
        ...     print(d[3])
        3

    If there is a way to break dict like behavior and you can reproduce it, please
    report it to `the GitHub issues <https://github.com/cdusold/PySpeedup/issues/>`_.

    .. note:: This class is not thread safe, nor is it process safe. Any multithreaded
              or multiprocessed uses of this class holds no guarantees of accuracy.

    You can configure how this class stores things in a few ways.

    The file_basename parameter allows you to keep multiple different stored objects
    in the same file_location, which defaults to .PySpeedup in the user's home folder.
    Using a file_basename of the empty string may cause a small slowdown if more
    than just this object's files are in the folder. Using a file_location of the
    empty string will result in files being placed in the environment's current
    location (i.e. what `os.getcwd()` would return).

    The size_limit parameter determines how many items are kept in each page, and the
    max_pages parameter determines how many pages can be kept in memory at the same
    time. If you use smaller items in the dict, increasing either is probably a
    good idea to get better performance. This setting will only use about 128 MB if
    standard floats or int32 values. Likely less than 200 MB will ever be in memory,
    which prevents the RAM from filling up and needing to use swap space. Tuning
    these values will be project, hardware and usage specific to get the best results.
    Even with the somewhat low defaults, this will beat out relying on python to
    use swap space.
    """
    def __init__(self, file_basename, size_limit = 1024, max_pages = 16, file_location = join(expanduser("~"),".PySpeedup")):
        if max_pages < 1:
            raise ValueError("There must be allowed at least one page in RAM.")
        self.max_pages = max_pages
        if size_limit < 1:
            raise ValueError("There must be allowed at least one item per page.")
        self.size_limit = size_limit
        if file_location:
            try:
                makedirs(file_location)
            except OSError as e:
                if e.errno != 17:
                    raise
                pass
        self._file_base = join(file_location,file_basename)
        self.pages = _page()
        self._length = 0
        self._total = set()
        self._queue = []
        try:
            with open(self._file_base+'Len', 'rb') as f:
                self.pages.currentDepth,self._length = pickle.load(f)
            for f in glob(self._file_base+'*'):
                try:
                    self._total.add(int(f[len(self._file_base):]))
                except:
                    pass
        except:
            pass
        atexit.register(_exitgracefully,self)
    def _guarantee_page(self,k):
        """
        Pulls up the page in question.
        """
        if k not in self.pages:
            try:
                if k in self._total:
                    self._load_page_from_disk(k)
            except:
                pass
            if k not in self.pages:
                self.pages[k]=_page()
                self._total.add(k)
                self.pages[k].currentDepth=self.pages.currentDepth
                self._queue.append(k)
        while len(self._queue)>self.max_pages:
            if self._queue[0] == k:
                self._queue.append(self._queue[0])
                del self._queue[0]
            self._save_page_to_disk(self._queue[0])
    def _branchpage(self,pagenumber):
        self._guarantee_page(pagenumber)
        if self.pages[pagenumber].currentDepth == self.pages.currentDepth:
            return
        self.pages[pagenumber].currentDepth = self.pages.currentDepth
        for key in set(self.pages[pagenumber].keys()):
            k = hash(key)&self.pages.currentDepth
            if k != pagenumber:
                self._guarantee_page(pagenumber)
                v = self.pages[pagenumber][key]
                del self.pages[pagenumber][key]
                self._guarantee_page(k)
                self.pages[k][key]=v
    def _finditem(self,key):
        """
        Pulls up the page containing the key in question.

        Most frequently O(1), when a page becomes too large, there's
        a O(ln(n)) search that refactors O(k ln(n)) elements
        once every O(k) insertions. A full refactor usually
        happens in strides, moving a total of O(n) elements
        split up over O(ln(n)) calls. This makes the worst
        time refactor O(n) and usual refactor approximately
        O(n/ ln(n)). Average case lookup O(n/k).
        """
        k=hash(key)&self.pages.currentDepth
        i = 0
        while (k&(self.pages.currentDepth>>i)) not in self._total|set([0]):
            i+=1
        self._branchpage(k&(self.pages.currentDepth>>i))
        self._guarantee_page(k)
        return k,key
    def _iterpages(self):
        """
        Pulls up page after page and cycles through all of them.
        """
        for k in list(self._total):
            self._guarantee_page(k)
            yield self.pages[k]
    def __delitem__(self,key):
        '''
         Deletes the key value in question from the pages.
        '''
        i,k = self._finditem(key)
        del self.pages[i][k]
        self._length-=1
    def __getitem__(self,key):
        '''
         Retrieves the value the key maps to.
        '''
        i,k = self._finditem(key)
        return self.pages[i][k]
    def __iter__(self):
        '''
         Iterates through all the keys stored.
        '''
        for p in self._iterpages():
            for i in p:
                yield i
    def __len__(self):
        '''
         Returns the number of key value pairs stored.
        '''
        return self._length
    def __setitem__(self,key,value):
        '''
         Sets a value that a key maps to.
        '''
        i,k = self._finditem(key)
        if k not in self.pages[i]:
            self._length+=1
        self.pages[i][k]=value
        if len(self.pages[i]) > self.size_limit:
            if self.pages[i].currentDepth == self.pages.currentDepth:
                self.pages.currentDepth <<= 1
                self.pages.currentDepth  |= 1
            self._branchpage(i)
    def __del__(self):
        '''
        Save all the values to disk before closing.
        '''
        if self is None or not hasattr(self,"_save_page_to_disk") or self._file_base is None:
            return
        while len(self.pages)>0:
            for key in self.pages.keys():
                self._save_page_to_disk(key)
    def _save_page_to_disk(self,number):
        with open(self._file_base+'Len', 'wb') as f:
            pickle.dump((self.pages.currentDepth,self._length),f)
        if self._file_base:
            if number in self.pages:
                if len(self.pages[number])>0:
                    with open(self._file_base+str(number),'wb') as f:
                        pickle.dump(self.pages[number],f)
                else:
                    self._total.remove(number)
                del self.pages[number]
            for i in range(len(self._queue)):
                if self._queue[i] == number:
                    del self._queue[i]
                    break
    def _load_page_from_disk(self,number):
        if self._file_base:
            with open(self._file_base+str(number),'rb') as f:
                self.pages[number] = pickle.load(f)
            self._queue.append(number)
            remove(self._file_base+str(number))
    def __str__(self):
        return "Dictionary with values stored to "+self._file_base
    def __repr__(self):
        return "DiskDict().link_to_disk('',"+str(self.size_limit)+','+str(self.max_pages)+','+self._file_base+')'
    def __contains__(self, item):
        i,k = self._finditem(item)
        return k in self.pages[i]
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_val, trace):
        _exitgracefully(self)


if __name__ == '__main__':
    d = DiskDict('testDiskDict',2,2)
    for i in range(16):
        d[i/10.]=i
        print(d.pages)
    d.max_pages=16
    for i in range(16):
        d[i/10.]=i
        print(d.pages)
