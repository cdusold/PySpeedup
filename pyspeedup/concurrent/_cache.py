from types import FunctionType
import traceback
from marshal import dumps
from marshal import loads
from functools import partial
from multiprocessing import Queue
from multiprocessing import Process
from multiprocessing import Manager

class _StillWaiting():
    pass
def _parallelRun(a_queue,a_dict,a_func_marshal,a_func_name,a_task, an_event):
    '''This runs a function, piping recursive calls to the _taskManager through a provided Queue.'''
    try:
        a_func=FunctionType(loads(a_func_marshal),globals(),"a_func")
        globals()[a_func_name]=partial(_getValue,a_dict,a_queue,an_event,True,a_func)
        globals()[a_func_name].apply_async=partial(_getValue,a_dict,a_queue,an_event,False,a_func)
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
def _taskManager(a_queue,a_dict,a_func_marshal,a_func_name,an_event):
    '''The method the asynchronous.Cache runs to maintain exoprocess control of the cache.'''
    while True:
        a_task=a_queue.get()
        if a_task is not None:
            Process(target=_parallelRun,args=(a_queue,a_dict,a_func_marshal,a_func_name,a_task,an_event)).start()
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
        self.func=FunctionType(loads(self._f),globals(),"a_func")
        globals()[self._n]=partial(_getValue,self._d,self._q,self._e,True,self.func)
        globals()[self._n].apply_async=partial(_getValue,self._d,self._q,self._e,False,self.func)
        self._t=Process(target=_taskManager,args=(self._q,self._d,self._f,self._n, self._e))
        self._t.start()
    def apply_async(self,*item):
        return _getValue(self._d,self._q,self._e,False,self.func,*item)
    def __call__(self,*item):
        return _getValue(self._d,self._q,self._e,True,self.func,*item)
    def __del__(self):
        self._t.terminate()
    def __repr__(self):
        return 'concurrent.Cache('+self.func.__repr__()+')'