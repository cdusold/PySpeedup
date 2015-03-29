from collections import MutableSequence
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
class _page(list):
    pass
class DiskList(MutableSequence):
    """
    A list class that maintains O(k) look up and write while keeping RAM usage O(1) as well.
    """
    def __init__(self, *args, **kwargs):
        self.pages=dict()
        self.pages[0]=_page()
        self._length = len(self.pages[0])
        self._number_of_pages=1
        self._queue=[0]
        self._file_base = None
        for i in list(*args, **kwargs):
            self.append(i)
    def link_to_disk(self, file_basename, size_limit = 1024, max_pages = 16, file_location = join(expanduser("~"),"PySpeedup")):
        if len(self)>0:
            raise Exception("Linking to disk should happen before any data is written.")
        if self._file_base:
            raise Exception("Can't link to two file names or locations at the same time.")
        self._file_base = join(file_location,file_basename)
        self._size_limit = size_limit
        self.max_pages = max_pages
        try:
            with open(self._file_base+'Len', 'rb') as f:
                self._number_of_pages,self._length = cPickle.load(f)
                self._queue=[]
                del self.pages[0]
        except:
            pass
        atexit.register(_exitgracefully,self)
        return self
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
                break
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
        k,i=divmod(key,self._size_limit)
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
        if self is None or not hasattr(self,"_save_page_to_disk"):
            return
        while len(self.pages)>0:
            for key in self.pages.keys():
                self._save_page_to_disk(key)
    def _save_page_to_disk(self,number):
        import cPickle
        with open(self._file_base+'Len', 'wb') as f:
            cPickle.dump((self._number_of_pages,self._length),f)
        if self._file_base:
            if number in self.pages:
                if len(self.pages[number])>0:
                    with open(self._file_base+str(number),'wb') as f:
                        cPickle.dump(self.pages[number],f)
                else:
                    self._number_of_pages-=1
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
        return "List with values stored to "+self._file_base
    def __repr__(self):
        return "DiskList().link_to_disk('',"+str(self._size_limit)+','+str(self.max_pages)+','+self._file_base+')'
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
        k = self._length//self._size_limit
        if k == self._number_of_pages:
            self._newpage()
        self._guarantee_page(k)
        self.pages[k].append(v)
        self._length+=1
    def insert(self,i,v):
        k,i = divmod(i,self._size_limit)
        if k == self._number_of_pages:
            self._newpage()
        self.pages[k].insert(i,v)
        if len(self.pages[k])>self._size_limit:
            for k in range(k,self._number_of_pages-1):
                self._guarantee_page(i)
                v = self.pages[i][-1]
                del self.pages[i][-1]
                self._guarantee_page(i+1)
                self.pages[i+1].insert(0,v)
            if len(self.pages[self._number_of_pages-1])>self._size_limit:
                self._newpage()
                self.pages[self._number_of_pages-1].append(self.pages[self._number_of_pages-2][-1])
                del self.pages[self._number_of_pages-2][-1]
        self._length+=1


if __name__ == '__main__':
    d = DiskList()
    d.link_to_disk('testDiskList',2,2)
    while len(d):
        d.pop()
    for i in range(16):
        d.append(i)
        print(d.pages)
    d.max_pages=16
    for i in range(16):
        d[i]=i
        print(d.pages)