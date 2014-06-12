from multiprocessing import Queue
from multiprocessing import Process
from multiprocessing import Manager
from marshal import dumps
from marshal import loads
from types import FunctionType
from functools import partial

def _generatorFromResults(a_list,an_event):
    i=0
    while True:
        try:
            yield a_list[i]
            i+=1
        except:
            an_event.wait(.1)
    raise Exception("Deadlocked...")
def _run(a_queue,a_gen_marshal,a_gen_name,a_list,an_event):
    try:
        a_generator=FunctionType(loads(a_gen_marshal),globals(),"a_func")
        globals()[a_gen_name]=partial(_generatorFromResults,a_list,an_event)
        for each_value in a_generator():
            a_queue.put(each_value)
    except Exception as e:
        print("Dunno what to tell you bud: {}".format(str(e)))
class Buffer():
    "Current implementation requires the values be uniformly increasing (like the primes, or positive fibonnaci sequence)."
    def __init__(self,generator,buffersize=16,haltCondition=None):
        self._generator,self._buffersize=generator,buffersize
        self._m=Manager()
        self._e=self._m.Event()
        self._g=dumps(generator.__code__)
        self._n=generator.__name__
        self._cache=self._m.list()
        #self.set_halt_condition(haltCondition) #This will make non-uniformly increasing generators usable without introducing a halting problem in the code (just in the userspace).
        self._q=Queue(self._buffersize)
        self._thread=Process(target=_run,args=(self._q,self._g,self._n,self._cache,self._e))
        self._thread.daemon=True
        self._thread.start()
    def __del__(self):
        self._thread.terminate()
        del self._thread
    def __call__(self):
        i=0
        while True:
            try:
                yield self._cache[i]
                i+=1
            except:
                self._e.wait(.1)
                self.pull_values()
        raise Exception("Deadlocked...")
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
                if self._q.empty():
                    self._e.wait(.1)
                    self._e.clear()
                else:
                    try:
                        self._cache.append(self._q.get(True,10))
                        cache_len+=1
                        self._e.set()
                        self._e.clear()
                        if cache_len==key+1:
                            return self._cache[key]
                    except:
                        print("Starts failing at {}. Manager debug info is {}.".format(cache_len, self._m._debug_info()))
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