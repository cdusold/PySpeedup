import random as rnd
import time
import unittest as ut
import copy
import operator

class _Cached:
    "This will shine the most with recursive functions. But the recursion has to call the cached function, not the function itself."
    f=None
    n=0
    c=None
    pop=None
    def popRandom(self):
        del self.c[rnd.choice(list(self.c.keys()))]
    def __init__(self,function, numberOfCachedValues, popType='random'):
        for n in list(n for n in set(dir(function)) - set(dir(self)) if n != '__class__'):
            setattr(self, n, getattr(function, n))
        self.f=function
        self.n=numberOfCachedValues
        self.c={}
        if popType=='random':
            self.pop=self.popRandom
    def __call__(self,*args, **kwargs):
        i=str(args)+str(kwargs)
        if i in self.c:
            return copy.deepcopy(self.c[i])
        else:
            t=self.f(*args,**kwargs)
            if len(self.c)>=self.n and self.n!=-1:
                self.pop()
            self.c[i]=copy.deepcopy(t)
            return t
def cached(numberOfCachedValues, popType='random'):
    '''A decorator that creates a simplistic cached function with minimal overhead.'''
    def decorator(f):
        return _Cached(f,numberOfCachedValues,popType)
    return decorator
            
class Polynomial():
    "This class utilizes dict of keys sparse polynomial implementation."
    _d={}
    _max=-1
    def __init__(self,*args,**kwargs):
        if len(kwargs)>0:
            self._d=kwargs
        if len(args)>0:
            self._max=args[0]
            if len(args)>1:
                max=self._max
                if len(args)>2:
                    max=args[2]
                for i in range(0,max+args[1],args[1]):
                    self._d[i]=1
    def __add__(self,other):
        out={}
        for i in set(self.keys()).union(set(other.keys())):
            out[i]=self._d.get(i,0)+other._d.get(i,0)
        return Polynomial(**out)
    def __iadd__(self,other):
        for i in set(self.keys()).union(set(other.keys())):
            self._d[i]=self._d.get(i,0)+other._d.get(i,0)
        return self
    def __sub__(self,other):
        out={}
        for i in set(self.keys()).union(set(other.keys())):
            out[i]=self._d.get(i,0)-other._d.get(i,0)
        return Polynomial(**out)
    def __iadd__(self,other):
        for i in set(self.keys()).union(set(other.keys())):
            self._d[i]=self._d.get(i,0)-other._d.get(i,0)
        return self
    def __mul__(self,other):
        out={}
        for i in self.keys():
            for j in other.keys():
                if max>0 and i+j>max:
                    continue
                out[i+j]=out.get(i+j,0)+self[i]*other[j]

class Timer:    
    def __enter__(self):
        self.start = time.clock()
        return self
    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start
        
#Cache this. Multiprocessed would work decently, although it's less necessary.
@cached(100)
def fibonacci(n): #Source: http://stackoverflow.com/a/14782458/786020
    """Compute the nth Fibonacci number."""
    if n<0:
        raise Exception("Reverse fibonacci sequence not implemented.")
    if n <= 3:
        return (0, 1, 1, 2)[n]
    elif n % 2 == 0:
        a = fibonacci(n // 2 - 1)
        b = fibonacci(n // 2)
        return ((2 * a + b) * b)
    else:
        a = fibonacci(n // 2)
        b = fibonacci(n // 2 + 1)
        return (a * a + b * b)

def uncachedFib(a):
    if a in [0,1]:
        return a
    if a<0:
        raise Exception("Reverse fibonacci sequence not implemented.")
    return uncachedFib(a-1)+uncachedFib(a-2)
    
class cachedTest(ut.TestCase):
    c=None
    def setUp(self):
        @cached(1)
        def fib(a):
            if a in [0,1]:
                return a
            if a<0:
                raise Exception("Reverse fibonacci sequence not implemented.")
            return fib(a-1)+fib(a-2)
        self.c=fib
    def test_fib(self):
        self.assertEqual(self.c(0),0,"The zeroth element of the Fibonnaci sequence is 0, not {}.".format(str(self.c(0))))
        self.assertEqual(self.c(1),1,"The first element of the Fibonnaci sequence is 1, not {}.".format(str(self.c(1))))
        self.assertEqual(self.c(2),1,"The second element of the Fibonnaci sequence is 1, not {}.".format(str(self.c(2))))
        self.assertEqual(self.c(3),2,"The third element of the Fibonnaci sequence is 2, not {}.".format(str(self.c(3))))
        self.assertEqual(self.c(4),3,"The fourth element of the Fibonnaci sequence is 3, not {}.".format(str(self.c(4))))
        self.assertEqual(self.c(5),5,"The fifth element of the Fibonnaci sequence is 5, not {}.".format(str(self.c(5))))
        #self.assertRaises(f(-1)
    def test_init(self):
        self.assertEqual(len(self.c.c),0,"The cache was malformed.")
        self.assertEqual(self.c.n,1,"The cache max size was not recorded properly.")
        self.assertEqual(self.c.f(0),uncachedFib(0),"The function was not entered correctly.")
    def test_cache(self):
        i=self.c(0)
        self.assertEqual(len(self.c.c),1,"The value was not cached properly.")
        self.assertEqual(self.c(0),i,"The cached answer was incorrect.")
    def test_pop(self):
        self.c.n=3
        i=self.c(3)
        self.assertEqual(len(self.c.c),3,"Recursion not properly set up for caching.")
        i=self.c(4)
        self.assertEqual(len(self.c.c),3,"Maximum cache size not implemented correctly.")
    def test_speed(self):
        t1=None
        t2=None
        with Timer() as t1:
            k=uncachedFib(32)
        self.c.n=-1
        with Timer() as t2:
            k=self.c(32)
        self.assertLess(t2.interval,t1.interval,"There isn't a speed up... This is useless then, I suppose.")
        with Timer() as t1:
            k=self.c(32)
        self.assertGreater(t2.interval,t1.interval,"There isn't a speed up... This is useless then, I suppose.")

@cached(10000)     
def gcd(a,b):
    r=a%b
    if r==0:
        return b
    else:
        return gcd(b,r)

def f(q):
    for i in range(100):
        q.append(i**2)
        time.sleep(.25)

def func(size,max,min):
    if size<min:
        return 1 #Empty
    if size<max:
        return func(size,size,min)
    if size<max+min:
        return size-max+2
    count=func(size,max-1,min)
    for i in range(size-max+1):
        count+= 2 * func(i,max,min)
    return count

if __name__ == '__main__':
    ut.main()
