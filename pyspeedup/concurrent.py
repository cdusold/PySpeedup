from multiprocessing import Queue as _Queue
from multiprocessing import Process as _Process
from multiprocessing import Manager as _Manager
import traceback as _traceback
from marshal import dumps as _dumps
from marshal import loads as _loads
from types import FunctionType as _FunctionType
from functools import partial as _partial

__all__=['Cache','Buffer','buffer']

class _StillWaiting():
    pass
def _parallelRun(a_queue,a_dict,a_func_marshal,a_func_name,a_task, an_event):
    '''This runs a function, piping recursive calls to the _taskManager through a provided Queue.'''
    try:
        a_func=_FunctionType(_loads(a_func_marshal),globals(),"a_func")
        globals()[a_func_name]=_partial(_getValue,a_dict,a_queue,an_event,True)
        globals()[a_func_name].apply_async=_partial(_getValue,a_dict,a_queue,an_event,False)
        a_result=a_func(*a_task)
        a_dict[a_task]=a_result
        an_event.set()
        an_event.clear()
    except:
        _traceback.print_exc()
        a_dict[a_task]=None
        an_event.clear()
def _getValue(a_dict,a_queue,an_event,wait,*item):
    '''This gets the cached value for a task, or submits a new job and waits on it to complete.'''
    if item not in a_dict:
        a_dict[item]=_StillWaiting
        a_queue.put(item)
    if not wait:
        return a_dict[item]
    temp=a_dict[item]
    while temp is _StillWaiting:
        an_event.wait(.1)
        temp=a_dict[item]
    return temp
def _taskManager(a_queue,a_dict,a_func_marshal,a_func_name,an_event):
    '''The method the asynchronous.Cache runs to maintain exoprocess control of the cache.'''
    while True:
        a_task=a_queue.get()
        if a_task is not None:
            _Process(target=_parallelRun,args=(a_queue,a_dict,a_func_marshal,a_func_name,a_task,an_event)).start()
class Cache():
    '''An asynchronous cache implementation. Maintains multiple recursive calls stably.'''
    def __init__(self,func):
        for n in list(n for n in set(dir(func)) - set(dir(self)) if n != '__class__'):
            setattr(self, n, getattr(func, n))
        self._m=_Manager()
        self._e= self._m.Event()
        self._d=self._m.dict()
        self._f=_dumps(func.__code__)
        self._n=func.__name__
        self._q=_Queue()
        self._t=_Process(target=_taskManager,args=(self._q,self._d,self._f,self._n, self._e))
        self._t.start()
    def apply_async(self,*item):
        return _getValue(self._d,self._q,self._e,False,*item)
    def __call__(self,*item):
        return _getValue(self._d,self._q,self._e,True,*item)
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
        self._q=_Queue(self._buffersize)
        self._thread=_Process(target=_run,args=(self._q,generator))
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

def factor(N):
    '''Runs multiple tests concurrently, starting with Monte Carlo primality testing, and ending with eliptic curves.'''
    #Ideally, a Prime-biased (Certificates) and Composite-biased (http://en.wikipedia.org/wiki/Baillie-PSW_primality_test) Monte Carlo test compete, and the first one to return a guaranteed answer stops the other.
    #Then brute-force prime(using concurrent buffer, likely, and a disk-complemented cache)<sqrt(N) checker for low hanging fruit, as they say...
    #Then start Pollard-Rho, so higher fruit...
    #Then Pollard p-1...
    #Then quadratic?
    #Then elliptic curves?
    #For each of these, if the montecarlo returns Prime IMMEDIATELY KILL, and return [1,N]
    #If any algorithm find a factor, kill the rest, and start factoring it and N divided by it concurrently.
    pass            

if __name__=='__main__':
    @Cache
    def _func(size,max,min):
        '''A test function.'''
        if size<min or max<min:
            return 1 #Empty
        if size<max:
            return _func(size,size,min)
        count=_func(size,max-1,min)
        if max==size:
            return count+1
        for i,j in enumerate(range(size-max,-1,-1)):
            count+= _func(i-1,max-1,min) * _func(j-1,max,min)
        return count
    def postponed_sieve():                   # postponed sieve, by Will Ness      
        yield 2; yield 3; yield 5; yield 7;  # original code David Eppstein, 
        D = {}                               #            ActiveState Recipe 2002
        ps = (p for p in postponed_sieve())  # a separate Primes Supply:
        p = next(ps) and next(ps)            # (3) a Prime to add to dict
        q = p*p                              # (9) when its sQuare is 
        c = 9                                # the next Candidate
        while True:
            if c not in D:                   # not a multiple of any prime seen so far:
                if c < q: yield c            #   a prime, or
                else:                        #   (c==q) next prime's square:
                    add(D,c + 2*p,2*p)       #     (9+6,6 : 15,21,27,33,...)
                    p=next(ps)               #     (5)
                    q=p*p                    #     (25)
            else:                            # a composite:
                s = D.pop(c)                 #   step of increment
                add(D,c + s,s)               #   next multiple, same step
            c += 2                           # next odd candidate
    @buffer()
    def concurrent_sieve():                  # postponed sieve, by Will Ness
        yield 2; yield 3; yield 5; yield 7;  # original code David Eppstein, 
        D = {}                               #            ActiveState Recipe 2002
        ps = (p for p in postponed_sieve())  # a separate Primes Supply:
        p = next(ps) and next(ps)            # (3) a Prime to add to dict
        q = p*p                              # (9) when its sQuare is 
        c = 9                                # the next Candidate
        while True:
            if c not in D:                   # not a multiple of any prime seen so far:
                if c < q: yield c            #   a prime, or
                else:                        #   (c==q) next prime's square:
                    add(D,c + 2*p,2*p)       #     (9+6,6 : 15,21,27,33,...)
                    p=next(ps)               #     (5)
                    q=p*p                    #     (25)
            else:                            # a composite:
                s = D.pop(c)                 #   step of increment
                add(D,c + s,s)               #   next multiple, same step
            c += 2                           # next odd candidate

    def add(D,x,s):                          # make no multiple keys in Dict
        while x in D: x += s                 # increment by the given step
        D[x] = s    
    primes=concurrent_sieve
    for i in range(10):
        print(str(primes[i]))
    for i in range(20):
        print(str(primes[i]))
    defaultPrimer=postponed_sieve()
    for i in range(100000):
        assert next(defaultPrimer)==primes[i]
    print("Success!")
    del primes
    print(str(_func(7,7,3)))
    del _func