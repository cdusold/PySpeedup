from multiprocessing import Queue,Process,Manager
import traceback
from marshal import dumps,loads
from types import FunctionType
from functools import partial

__all__=['Cache','Buffer','buffer']

class StillWaiting():
    pass
def parallelRun(a_queue,a_dict,a_func_marshal,a_func_name,a_task, an_event):
    '''This runs a function, piping recursive calls to the taskManager through a provided Queue.'''
    try:
        a_func=FunctionType(loads(a_func_marshal),globals(),"a_func")
        globals()[a_func_name]=partial(getValue,a_dict,a_queue,an_event)
        a_result=a_func(*a_task)
        a_dict[a_task]=a_result
        an_event.set()
        an_event.clear()
    except:
        traceback.print_exc()
        a_dict[a_task]=None
        an_event.clear()
def getValue(a_dict,a_queue,an_event,*item):
    '''This gets the cached value for a task, or submits a new job and waits on it to complete.'''
    if item not in a_dict:
        a_dict[item]=StillWaiting
        a_queue.put(item)
    temp=a_dict[item]
    while temp is StillWaiting:
        an_event.wait(.1)
        temp=a_dict[item]
    return temp
def taskManager(a_queue,a_dict,a_func_marshal,a_func_name,an_event):
    '''The method the asynchronous.Cache runs to maintain exoprocess control of the cache.'''
    while True:
        a_task=a_queue.get()
        if a_task is not None:
            Process(target=parallelRun,args=(a_queue,a_dict,a_func_marshal,a_func_name,a_task,an_event)).start()
class Cache():
    '''An asynchronous cache implementation. Maintains multiple recursive calls stably.'''
    def __init__(self,func):
        for n in list(n for n in set(dir(func)) - set(dir(self)) if n != '__class__'):
            setattr(self, n, getattr(func, n))
        self._m=Manager()
        self._e= self._m.Event()
        self._d=self._m.dict()
        self._f=dumps(func.__code__)
        self._n=func.__name__
        self._q=Queue()
        self._t=Process(target=taskManager,args=(self._q,self._d,self._f,self._n, self._e))
        self._t.start()
    def apply_async(self,*item):
        self._d[item]=StillWaiting
        self._q.put(item)
        #print("Starting {}...".format(str(item)))
    def __call__(self,*item):
        return getValue(self._d,self._q,self._e,*item)
    def __del__(self):
        self._t.terminate()
    def __repr__(self):
        return 'concurrent.Cache('+self.func.__repr__()+')'
        
def _run(a_queue,a_generator):
    try:
        for each_value in a_generator():
            a_queue.put(each_value)
    except Exception as e:
        print("Dunno what to tell you bud: {}".format(str(e)))
class Buffer():
    "Current implementation requires the values be uniformly increasing (like the primes, or positive fibonnaci sequence)."
    def __init__(self,generator,buffersize=16,haltCondition=None):
        self._generator,self._buffersize=generator,buffersize
        self._cache=[]
        #self.set_halt_condition(haltCondition) #This will make non-uniformly increasing generators usable without introducing a halting problem in the code (just in the userspace).
        self._q=Queue(self._buffersize)
        self._thread=Process(target=_run,args=(self._q,generator))
        self._thread.daemon=True
        self._thread.start()
    def __del__(self):
        self._thread.terminate()
        del self._thread
    def __contains__(self,item):
        currentCount=len(self._cache)
        if item in self._cache[:currentCount]:
            return True 
        else:
            if self._cache[currentCount]>item:
                return False
            else:
                currentCount+=1
                while self[currentCount]<item:
                    currentCount+=1
                return self[currentCount]==item
    def __getitem__(self,key):
        cache_len=len(self._cache)
        if key+self._buffersize>cache_len:
            self.pull_values()
        if key<cache_len:
            return self._cache[key]
        else:
            while True:
                self._cache.append(self._q.get(True,60))
                cache_len+=1
                if cache_len==key+1:
                    return self._cache[key]
    def pull_values(self):
        try:
            for i in range(self._buffersize):
                self._cache.append(self._q.get(False))
        except Exception as e:
            pass
    def __repr__(self):
        return 'concurrent._Buffer('+self.func.__repr__()+','+str(self._buffersize)+',None)'
def buffer(buffersize=16,haltCondition=None):
    '''A decorator to create a concurrently buffered generator.'''
    def decorator(f):
        return Buffer(f,buffersize,haltCondition)
    return decorator

def func(size,max,min):
    '''A test function.'''
    if size<min or max<min:
        return 1 #Empty
    if size<max:
        return func(size,size,min)
    count=func(size,max-1,min)
    if max==size:
        return count+1
    for i,j in enumerate(range(size-max,-1,-1)):
        count+= func(i-1,max-1,min) * func(j-1,max,min)
    return count
    
if __name__=='__main__':
    func=Cache(func)
    print(str(func(7,7,3)))
    del func