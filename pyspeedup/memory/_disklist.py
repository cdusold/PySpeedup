from collections import MutableSequence
import pickle
from os.path import expanduser,join
from os import remove, makedirs
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
class _page(list):
    pass
class DiskList(MutableSequence):
    """
    A list class that maintains O(k) look up and O(1) append while keeping RAM usage O(1) as well.
    Unfortunately, insert is O(n/k).

    This is accomplished through paging every size_limit consecutive values together
    behind the scenes.

    The object created can be used any way a normal list would be used, and will
    clean itself up on python closing. This means saving all the remaining pages
    to disk. If the file_basename and file_location was used before, it will load
    the old values back into itself so that the results can be reused.

    There are two ways to initialize this object, as a standard object:

        >>> diskList = DiskList("sample")
        >>> for i in range(10):
        ...     diskList.append(i)
        ...
        >>> diskList[3]
        3
        >>> ", ".join(str(x) for x in diskList)
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        >>> del diskList[5]
        >>> ", ".join(str(x) for x in diskList)
        0, 1, 2, 3, 4, 6, 7, 8, 9

    Or through context:

        >>> with DiskList("test") as d:
        ...     for i in range(10):
        ...         d.append(i)
        ...     print(d[3])
        3

    If there is a way to break list like behavior and you can reproduce it, please
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
    time. If you use smaller items in the list, increasing either is probably a
    good idea to get better performance. This setting will only use about 64 MB if
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
        self.pages=dict()
        self._length = 0
        self._number_of_pages = 0
        self._queue = []
        try:
            with open(self._file_base+'Len', 'rb') as f:
                self._number_of_pages,self._length = pickle.load(f)
        except:
            pass
        atexit.register(_exitgracefully,self)
    def _guarantee_page(self,k):
        """
        Pulls up the page in question.
        """
        if k not in self.pages:
            if k < self._number_of_pages:
                self._load_page_from_disk(k)
            else:
                raise IndexError("list assignment index out of range")
        while len(self._queue)>self.max_pages:
            if self._queue[0] == k:
                self._queue.append(self._queue[0])
                del self._queue[0]
            self._save_page_to_disk(self._queue[0])
    def _newpage(self):
        self.pages[self._number_of_pages]=[]
        self._queue.append(self._number_of_pages)
        self._number_of_pages+=1
    def _finditem(self,key):
        """
        Pulls up the page containing the key in question.
        """
        if key<0:
            key+=self._length
        if key >= self._length or key < 0:
            raise IndexError("list assignment index out of range")
        k,i=divmod(key,self.size_limit)
        self._guarantee_page(k)
        return k,i
    def _iterpages(self):
        """
        Pulls up page after page and cycles through all of them.
        """
        for k in range(self._number_of_pages):
            self._guarantee_page(k)
            yield self.pages[k]
    def __delitem__(self,key):
        '''
         Deletes the key value in question from the pages.
        '''
        i,k = self._finditem(key)
        del self.pages[i][k]
        self._length-=1
        for i in range(i,self._number_of_pages-1):
            self._guarantee_page(i+1)
            if self.pages[i+1]:
                v = self.pages[i+1][0]
                del self.pages[i+1][0]
                self._guarantee_page(i)
                self.pages[i].append(v)
        self._guarantee_page(self._number_of_pages-1)
        if not self.pages[self._number_of_pages-1]:
            del self.pages[self._number_of_pages-1]
            self._number_of_pages-=1
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
    def __reversed__(self):
        for p in reversed(range(self._number_of_pages)):
            for i in reversed(self.pages[p]):
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
        self.pages[i][k]=value
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
            pickle.dump((self._number_of_pages,self._length),f)
        if self._file_base:
            if number in self.pages:
                if len(self.pages[number])>0:
                    with open(self._file_base+str(number),'wb') as f:
                        pickle.dump(self.pages[number],f)
                else:
                    self._number_of_pages-=1
                del self.pages[number]
            for i in range(len(self._queue)):
                if self._queue[i] == number:
                    del self._queue[i]
                    break
    def _load_page_from_disk(self,number):
        if self._file_base:
            try:
                with open(self._file_base+str(number),'rb') as f:
                    self.pages[number] = pickle.load(f)
            except IOError as e:
                if e.errno != 2:
                    raise
                raise IOError(2, "Files got corrupted or removed, file " +
                                  str(number) + " no longer exists.")
            self._queue.append(number)
            remove(self._file_base+str(number))
    def __str__(self):
        return "List with values stored to "+self._file_base
    def __repr__(self):
        return "DiskList().link_to_disk('',"+str(self.size_limit)+','+str(self.max_pages)+','+self._file_base+')'
    def __contains__(self, item):
        try:
            i,k = self._finditem(key)
        except:
            return False
        return k in self.pages[i]
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_val, trace):
        _exitgracefully(self)
    def append(self,v):
        k = self._length//self.size_limit
        if k == self._number_of_pages:
            self._newpage()
        self._guarantee_page(k)
        self.pages[k].append(v)
        self._length+=1
    def insert(self,i,v):
        k,i = divmod(i,self.size_limit)
        if k == self._number_of_pages:
            self._newpage()
        self.pages[k].insert(i,v)
        if len(self.pages[k])>self.size_limit:
            for k in range(k,self._number_of_pages-1):
                self._guarantee_page(i)
                v = self.pages[i][-1]
                del self.pages[i][-1]
                self._guarantee_page(i+1)
                self.pages[i+1].insert(0,v)
            if len(self.pages[self._number_of_pages-1])>self.size_limit:
                self._newpage()
                self.pages[self._number_of_pages-1].append(self.pages[self._number_of_pages-2][-1])
                del self.pages[self._number_of_pages-2][-1]
        self._length+=1


if __name__ == '__main__':
    d = DiskList('testDiskList',2,2)
    while len(d):
        d.pop()
    for i in range(16):
        d.append(i)
        print(d.pages)
    d.max_pages=16
    for i in range(16):
        d[i]=i
        print(d.pages)
