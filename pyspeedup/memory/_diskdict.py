from collections import MutableMapping
import cPickle
from os.path import expanduser,join
from os import remove
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
            with open(self._file_base+'Len', 'rb') as f:
                self._length = cPickle.load(f)
        except:
            pass
        self._file_base = join(file_location,file_basename)
        self._total.remove(0)
        self._queue=[]
        self.size_limit = size_limit
        self.max_pages = max_pages
        del self.pages[0]
        for f in glob(self._file_base+'*'):
            try:
                self._total.add(int(f[len(self._file_base)]))
            except:
                pass
        if 0 not in self._total:
            self.pages[0]=_page()
            self._total.add(0)
            self._queue.append(0)
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
                break
            self._save_page_to_disk(self._queue[0])
    def _branchpage(self,pagenumber):
        self._guarantee_page(pagenumber)
        if self.pages[pagenumber].currentDepth == self.pages.currentDepth:
            return
        self.pages[pagenumber].currentDepth = self.pages.currentDepth
        for key in self.pages[pagenumber].keys():
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
        while (k&(self.pages.currentDepth>>i)) not in self._total:
            i+=1
        self._branchpage(k&(self.pages.currentDepth>>i))
        self._guarantee_page(k)
        return k,key
    def _iterpages(self):
        """
        Pulls up page after page and cycles through all of them.
        """
        for k in self._total:
            self._guarantee_page(k)
            yield self.pages[k]
    def __delitem__(self,key):
        '''
         Deletes the key value in question from the pages.
        '''
        i,k = self._finditem(key)
        if k in self.pages[i]:
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
        print i,len(self.pages[i])
        if len(self.pages[i]) > self.size_limit:
            if self.pages[i].currentDepth == self.pages.currentDepth:
                self.pages.currentDepth <<= 1
                self.pages.currentDepth  |= 1
            self._branchpage(i)
    def __del__(self):
        '''
        Save all the values to disk before closing.
        '''
        if self is None or not hasattr(self,"_save_page_to_disk"):
            return
        while len(self.pages)>0:
            for key in self.pages.keys():
                self._save_page_to_disk(key)
    def _save_page_to_disk(self,number):
        import cPickle
        with open(self._file_base+'Len', 'wb') as f:
            cPickle.dump(self._length,f)
        self._branchpage(number)
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
            os.remove(self._file_base+str(number))


if __name__ == '__main__':
    d = DiskDict()
    d.link_to_disk('test',2,2)
    for i in range(16):
        d[i/10.]=i
        print(d.pages)
    d.max_pages=16
    for i in range(16):
        d[i/10.]=i
        print(d.pages)