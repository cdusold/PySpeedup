from collections import MutableMapping
import cPickle
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
        for key in self.pages.keys():
            self._save_page_to_disk(key)
class _page(dict):
    currentDepth=0
class DiskDict(MutableMapping):
    """
    A dictionary class that maintains O(1) look up and write while keeping RAM usage O(1) as well.

    This is accomplished through a rudimentary (for now) hashing scheme to page the
    dictionary into parts.
    """
    def __init__(self, *args, **kwargs):
        self.pages=_page()
        self.pages[0]=_page(*args, **kwargs)
        self._length = len(self.pages[0])
        self._total={0}
        self._queue=[0]
        self._file_base = None
    def link_to_disk(self, file_basename, size_limit = 1024, max_pages = 16, file_location = join(expanduser("~"),"PySpeedup")):
        if len(self)>0:
            raise Exception("Linking to disk should happen before any data is written.")
        if self._file_base:
            raise Exception("Can't link to two file names or locations at the same time.")
        try:
            os.makedirs(file_location)
        except:
            pass
        self._file_base = join(file_location,file_basename)
        self.size_limit = size_limit
        self.max_pages = max_pages
        try:
            with open(self._file_base+'Len', 'rb') as f:
                self.pages.currentDepth,self._length = cPickle.load(f)
            self._total.remove(0)
            self._queue=[]
            del self.pages[0]
            for f in glob(self._file_base+'*'):
                try:
                    self._total.add(int(f[len(self._file_base):]))
                except:
                    pass
        except:
            pass
        atexit.register(_exitgracefully,self)
        return self
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
        import cPickle
        with open(self._file_base+'Len', 'wb') as f:
            cPickle.dump((self.pages.currentDepth,self._length),f)
        if self._file_base:
            if number in self.pages:
                if len(self.pages[number])>0:
                    with open(self._file_base+str(number),'wb') as f:
                        cPickle.dump(self.pages[number],f)
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
                self.pages[number] = cPickle.load(f)
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
    d = DiskDict()
    d.link_to_disk('testDiskDict',2,2)
    for i in range(16):
        d[i/10.]=i
        print(d.pages)
    d.max_pages=16
    for i in range(16):
        d[i/10.]=i
        print(d.pages)