"""
.. moduleauthor:: Chris Dusold <PySpeedup@chrisdusold.com>


"""
from types import FunctionType
import traceback
from marshal import dumps
from marshal import loads
from functools import partial
from multiprocessing import Queue
from multiprocessing import Process
from multiprocessing import Manager
import atexit

def _closeProcessGracefully(instance):
    if instance is not None:
        instance._q.put(_EndProcess)
        instance._q.close()
        instance._t.terminate()
        instance._t.join()
        instance._m.shutdown()
class _EndProcess():
    pass
class _StillWaiting():
    pass
def _parallelRun(a_queue,a_dict,a_func_marshal,a_func_name,a_task, an_event):
    '''This runs a function, piping recursive calls to the _taskManager through a provided Queue.'''
    try:
        a_func=FunctionType(loads(a_func_marshal),globals(),"a_func")
        globals()[a_func_name]=partial(_getValue,a_dict,a_queue,an_event,True,a_func)
        globals()[a_func_name].apply_async=partial(_getValue,a_dict,a_queue,an_event,False,a_func)
        globals()[a_func_name].batch_async=partial(_batchAsync,a_dict,a_queue,a_func)
        #setattr(globals()[a_func_name],"__contains__",a_dict.__contains__)
        a_result=a_func(*a_task)
        a_dict[a_task]=a_result
        an_event.set()
        an_event.clear()
    except:
        traceback.print_exc()
        a_dict[a_task]=None
        an_event.clear()
def _getValue(a_dict,a_queue,an_event,wait,func,*item):
    '''This gets the cached value for a task, or submits a new job and waits on it to complete.'''
    try:
        if not wait:
            return a_dict[item]
        temp=a_dict[item]
        while temp is _StillWaiting:
            an_event.wait(.1)
            temp=a_dict[item]
        return temp
    except:
        a_dict[item]=_StillWaiting
        if wait:
            a_dict[item]=func(*item)
            return a_dict[item]
        else:
            a_queue.put(item)
def _batchAsync(a_dict,a_queue,func,*items):
    '''This smartly decides how to branch asynchronously and does so synchronously if only one item is missing.'''
    items = [item for item in items if item not in a_dict]
    if len(items)>1:
        for item in items:
            a_dict[item]=_StillWaiting
            a_queue.put(item)
def _taskManager(a_queue,a_dict,a_func_marshal,a_func_name,an_event):
    '''The method the asynchronous.Cache runs to maintain exoprocess control of the cache.'''
    a_task = None
    while a_task is not (_EndProcess,):
        a_task=a_queue.get()
        if a_task is not (_EndProcess,) and a_task is not None:
            newThread = Process(target=_parallelRun,args=(a_queue,a_dict,a_func_marshal,a_func_name,a_task,an_event))
            newThread.daemon = True
            newThread.start()
class Cache():
    '''
    An asynchronous cache implementation. Maintains multiple recursive calls stably.

    The resultant object operates just like a function, but runs the code outside
    the main process. When calls are started with :meth:`~Cache.apply_async`, a new process
    is created to evaluate the call.

    A simple cache can reduce recursive functions such as the naive Fibonacci function
    to linear time in the input space, whereas a parallel cache can reduce certain
    problems even farther, depending on the layout of the call and the number of processors
    available on a computer. The code below demonstrates using :class:`Cache` as a simple
    cache::

        >>> @Cache
        ... def fibonacci(n):
        ...     if n < 2: # Not bothering with input value checking here.
        ...         return 1
        ...     return fibonacci(n-1)+fibonacci(n-2)
        ...
        >>> fibonacci(5)
        8

    Using cache to take advantage of the ability to handle recursion branching, that
    same code would become::

        >>> @Cache
        ... def fibonacci(n):
        ...     if n < 2: # Not bothering with input value checking here.
        ...         return 1
        ...     fibonacci.apply_async(n-1)
        ...     fibonacci.apply_async(n-2)
        ...     return fibonacci(n-1)+fibonacci(n-2)
        ...
        >>> fibonacci(100)
        573147844013817084101L

    .. note:: Be careful when picking how to call your functions if you are looking
              for speed. Given that the fibonacci sequence is roughly linear in
              dependencies with caching, there isn't a significant speedup. When in
              doubt, :mod:`cProfile` (or :mod:`profile`) are your friends.

    .. todo:: Eventually provide automatic profiling to help with this part.

    A good use for this would be in less sequential computation spaces, such as in
    factoring. When a pair of factors are found, each can be factored asynchronously
    to find all the prime factors recursively. When a factor in a factor pair is found
    that are known to be prime, or otherwise has its factors known, then only
    one needs to be factored further. At this point, blindly branching and factoring
    will have one side yield the cached value, and the other creating a new process.
    Given the Fibonacci example above, this will happen on every call that isn't the
    first call, yielding to `n` processes being spawned and using system resources.
    Simply caching the naive Fibonacci function is just about the fastest way to use it.

    To avoid unnecessary branching automatically, you can use the batch_async method
    similarly to the apply_async method, except each set of arguments, even if they're
    singular, must be wrapped in a tuple. Applying this to the Fibonacci function yields.

        >>> @Cache
        ... def fibonacci(n):
        ...     if n < 2: # Not bothering with input value checking here.
        ...         return 1
        ...     fibonacci.batch_async((n-1,),(n-2,))
        ...     return fibonacci(n-1)+fibonacci(n-2)
        ...
        >>> fibonacci(200)
        453973694165307953197296969697410619233826L

    This makes the branching optimal whenever possible. Race conditions might cause
    issues, but those caused by python's built in Manager cannot be mitigated easily.
    For the fibonnacci sequence, this will likely just revert the computation to a
    mostly synchronous and sequential calculation, which is optimal for this version
    of calculating the Fibonacci sequence.

    .. note:: There are `much better algorithms
              <http://en.wikipedia.org/wiki/Fibonacci_sequence#Matrix_form>`_ for
              calculating Fibonacci sequence elements; some of which are better suited
              for this type of caching.

    '''
#    Additionally, one can test whether a value has been calculated before by using
#    ``(*{item}) in {cache}``. Calls of this type will be faster if iterable objects
#    are passed to the ``in`` operator. This allows one to avoid unnecessary branching
#    and process creation. Using this, the same example becomes::
#
#        >>> @Cache
#        ... def fibonacci(n):
#        ...     if n < 2: # Not bothering with input value checking here.
#        ...         return 1
#        ...     if n-1 not in fibonacci or n-2 not in fibonacci:
#        ...         fibonacci.apply_async(n-1)
#        ...         fibonacci.apply_async(n-2)
#        ...     return fibonacci(n-1)+fibonacci(n-2)
#        ...
#        >>> fibonacci(5)
#        8

    def __init__(self,func):
        for n in list(n for n in set(dir(func)) - set(dir(self)) if n != '__class__'):
            setattr(self, n, getattr(func, n))
        setattr(self, "__doc__", getattr(func, "__doc__"))
        self._m=Manager()
        self._e= self._m.Event()
        self._d=self._m.dict()
        self._f=dumps(func.__code__)
        self._n=func.__name__
        self._q=Queue()
        self.func=FunctionType(loads(self._f),globals(),"a_func")
        globals()[self._n]=partial(_getValue,self._d,self._q,self._e,True,self.func)
        globals()[self._n].apply_async=partial(_getValue,self._d,self._q,self._e,False,self.func)
        globals()[self._n].batch_async=partial(_batchAsync,self._d,self._q,self.func)
        #setattr(globals()[self._n],"__contains__",self.__contains__)
        self._t=Process(target=_taskManager,args=(self._q,self._d,self._f,self._n, self._e))
        self._t.start()
        atexit.register(_closeProcessGracefully, self) #TODO: Make this line not necessary.
    def apply_async(self,*item):
        """
        Calling this method starts up a new process of the function call in question.
        This does not retrieve an answer.
        """
        return _getValue(self._d,self._q,self._e,False,self.func,*item)
    def batch_async(self,*items):
        """
        This method examines the arguments passed in for how to branch optimally
        then does so. This does not retrieve the answers, just like apply_async does not.
        The arguments must each be a complete set of the arguments passed into the function
        but in tuple form. If the cached function only takes one argument, wrap it with
        parenthesis and add a comma before the closing parenthesis.
        """
        _batchAsync(self._d,self._q,self.func,*items)
    def __call__(self,*item):
        return _getValue(self._d,self._q,self._e,True,self.func,*item)
    def __del__(self):
        _closeProcessGracefully(self)
    def __repr__(self):
        return 'concurrent.Cache('+self.func.__repr__()+')'
    #def __contains__(self,item):
    #    try:
    #        return tuple(item) in self._d
    #    except:
    #        return (item,) in self._d


if __name__ == "__main__":
    import doctest
    doctest.testmod()
