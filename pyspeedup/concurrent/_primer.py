'''This is a multifaceted concurrent system to do prime testing and factorization.

It is the motivation for the abstract multifacted concurrent system
(Which hasn't been abstracted out yet).

It also is the motivation for the concurrent disk dictionary
(which also isn't implemented yet.'''

from types import FunctionType
import traceback
from marshal import dumps
from marshal import loads
from functools import partial
from multiprocessing import Queue
from multiprocessing import Process
from multiprocessing import Manager
import math
import random
from pyspeedup.algorithms import gcd

#Todo: modify such that returns through queues, and quits or retries appropriately.
def StrongPrimeTest(n,t=2):
    '''Tests for primitivity using a strong primitivity test. Does not guarantee primitivity.'''
    if n==2:
        return True
    if n%2==0:
        return False
    m=n-1
    k=0
    while m%2==0:
        m//=2
        k+=1
    b=pow(t,m,n)
    if b==1:
        return True
    for i in range(0,k):
        if b==n-1:
            return True
        b=(b*b)%n
    return False
def BrutePrimitivityTest(n):
    '''Uses simple brute force calculation to determine primitivity.'''
    for i in range(2,int(math.sqrt(n)+1)):
        if n%i==0:
            return [i,n//i]
    return True
def pollard_p1(N):
    if N<=2:
        return [N]
    #B=int(math.pow(N,.2))
    B=1 #One will be added to this in the loop.
    M=math.factorial(B)
    a=random.randint(2,N-1) #Pick a random coprime.
    g=gcd(a,N) #Check that a is a coprime.
    while g==1 or g==N:
        B+=1
        M*=B
        g=gcd(pow(a,M,N)-1,N) #The pow function does efficient exponentiation mod N
    print(B)
    return [g,N//g]
def pollard_rho(N):
    if N<=2:
        return [N]
    def f(x):
        return (x*x+1)%N
    x=2
    y=2
    d=1
    c=0
    while d==1:
        x=f(x)
        y=f(f(y))
        d=gcd(abs(x-y),N)
        c+=1
    print(c)
    if d==N:
        return None #Using None to indicate failure.
    return [d,N//d]

#0=Guarantees composite, 1=guarantees primitivity, 2=generates factors
listOfAlgorithms=[(StrongPrimeTest,0),(BrutePrimitivityTest,0,1,2),(pollard_p1,0,1,2),(pollard_rho,0,1,2)]


#TODO: I stole the code from concurrent.Cache.
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
class Primer():
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