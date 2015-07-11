"""
.. moduleauthor:: Chris Dusold <PySpeedup@chrisdusold.com>


"""
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
def uniformlyNonDecreasing(buffer,item,attempts):
    """
    Stops after the buffer has seen a value larger than the one being searched for.
    The default halting condition for the Buffer class.
    """
    if self._cache[-1]>item:
        return True
    return False
def absolutelyNonDecreasing(buffer,item,attempts):
    """
    Stops after the buffer has seen an absolute value larger than the one being searched for.
    The example halting condition given in the documentation.
    """
    if abs(self._cache[-1])>abs(item):
        return True
    return False
class Buffer():
    """
    An implementation of a concurrent buffer that runs a generator in a
    separate processor.

    .. note:: The default halting condition requires the values be uniformly
              non decreasing (like the primes, or positive fibonnaci sequence).
              This halting condition is currently once the value reached is
              greater than or equal to the one being searched for.

    The resultant buffered object can be referenced as a list or an iterable.
    The easiest way to use this class is by utlizing the utility function
    :func:`~pyspeedup.concurrent.buffer`.

    For example, one can use it in the following way::

        >>> @buffer(4)
        ... def count():
        ...     i=0
        ...     while 1:
        ...         yield i
        ...         i+=1
        ...
        >>> count[0]
        0
        >>> count[15]
        15
        >>> for v,i in enumerate(count):
        ...     if v!=i:
        ...         print("Fail")
        ...     if v==5:
        ...         print("Success")
        ...         break
        ...
        Success

    It can also be used as a generator by calling the object like so::

        >>> for v,i in enumerate(count()):
        ...     if v!=i:
        ...         print("Fail")
        ...     if v==5:
        ...         print("Success")
        ...         break
        ...
        Success

    The sequence generated is cached, so the output stored will be static.

    To create your own halting condition, you need to provide a function with
    the first argument taken in as the buffer object, the second argument for
    the item that we're deciding whether we've passed (or given up on) during
    the search, and the third argument being how many times we've checked the
    halting condition during this search.

    For example, if your buffered sequence isn't uniformly non decreasing, but
    is instead absolutely non decreasing, you could create the following halting
    condition function:

        >>> def absolutelyNonDecreasing(buffer, item, attempts):
        ...     if abs(self._cache[-1])>abs(item):
        ...         return True
        ...     return False
        ...
        >>> @buffer(haltCondition = absolutelyNonDecreasing)
        ... def complexSpiral():
        ...     i = 1
        ...     while True:
        ...         yield i
        ...         i *= 1.1j
        ...
        >>> complexSpiral[1]
        1.1j
        >>> -1.21 in complexSpiral
        True

    Be careful in creating your halting condition, as if it is false for the
    sequence you are buffering, you may not see expected results, or you may
    find your program in an infinite loop. Be sure to consider asymptotes
    and other possibilities in your results. It may not be a bad idea to
    have it bail out after a certain number of attempts.

    .. note:: As of yet all values are stored in a list on the backend.
              There is no memory management built in to this version, but
              is planned to be integrated soon. Be careful not to accidentally
              cache too many or too large of values, as you may use up all of
              your RAM and slow down computation immensely.
    """
    def __init__(self,generator,buffersize=16,haltCondition=uniformlyNonDecreasing):
        for n in list(n for n in set(dir(generator)) - set(dir(self)) if n != '__class__'):
            setattr(self, n, getattr(generator, n))
        setattr(self, "__doc__", getattr(generator, "__doc__"))
        self._generator,self._buffersize=generator,buffersize
        self._m=Manager()
        self._e=self._m.Event()
        self._g=dumps(generator.__code__)
        self._n=generator.__name__
        self._cache=self._m.list()
        self.haltCondition = haltCondition #This will make non-uniformly increasing generators usable without introducing a halting problem in the code (just in the userspace).
        self._q=Queue(self._buffersize)
        self._thread=Process(target=_run,args=(self._q,self._g,self._n,self._cache,self._e))
        self._thread.daemon=True
        self._thread.start()
    def __del__(self):
        self._thread.terminate()
        del self._thread
    def __call__(self):
        """ Creates a generator that yields the values from the original
        starting with the first value.

        """
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
        attempts = 0
        prevCount = 0
        while self.haltCondition(self,item,attempts):
            currentCount=len(self._cache)
            if currentCount == prevCount:
                currentCount += 1
                self[prevCount]
            if item in self._cache[prevCount:currentCount]:
                return True 
            prevCount = currentCount
            attempts += 1
        currentCount=len(self._cache)
        if item in self._cache[prevCount:currentCount]:
            return True 
        return False
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
        """ A utility method used to pull and cache values from the
        concurrently run generator.

        """
        try:
            for i in range(self._buffersize):
                self._cache.append(self._q.get(False))
        except Exception as e:
            pass
    def __repr__(self):
        return 'concurrent._Buffer('+self.func.__repr__()+','+str(self._buffersize)+',None)'
def buffer(buffersize=16,haltCondition=uniformlyNonDecreasing):
    '''A decorator to create a concurrently buffered generator.

    Used with ``@buffer([buffersize,[haltCondition]])`` as described in :class:`~pyspeedup.concurrent.Buffer`'s documentation.
    '''
    def decorator(f):
        return Buffer(f,buffersize,haltCondition)
    return decorator


if __name__ == "__main__":
    import doctest
    doctest.testmod()
