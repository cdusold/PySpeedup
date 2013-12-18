import random as rnd
import time
import unittest as ut
import copy
import operator
from multiprocessing import Queue,Process,Manager,Pool
from multiprocessing.pool import ApplyResult

class _Cached:
    "This will shine the most with recursive functions. But the recursion has to call the cached function, not the function itself."
    f=None
    n=0
    c=None
    pop=None
    def popRandom(self):
        del self.c[rnd.choice(list(self.c.keys()))]
    def __init__(self,function, numberOfCachedValues, popType='random'):
        for n in set(dir(func)) - set(dir(self)):
            setattr(self, n, getattr(func, n))
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
        return _Cached(f,buffersize,haltCondition)
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

def fib(a):
    if a in [0,1]:
        return a
    if a<0:
        raise Exception("Reverse fibonacci sequence not implemented.")
    return fib(a-1)+fib(a-2)
def Fib(a):
    if a in [0,1]:
        return a
    if a<0:
        raise Exception("Reverse fibonacci sequence not implemented.")
    return fib(a-1)+fib(a-2)
    
class cachedTest(ut.TestCase):
    c=None
    def setUp(self):
        self.c=None
    def test_fib(self):
        self.assertEqual(fib(0),0,"The zeroth element of the Fibonnaci sequence is 0, not {}.".format(str(fib(0))))
        self.assertEqual(fib(1),1,"The first element of the Fibonnaci sequence is 1, not {}.".format(str(fib(1))))
        self.assertEqual(fib(2),1,"The second element of the Fibonnaci sequence is 1, not {}.".format(str(fib(2))))
        self.assertEqual(fib(3),2,"The third element of the Fibonnaci sequence is 2, not {}.".format(str(fib(3))))
        self.assertEqual(fib(4),3,"The fourth element of the Fibonnaci sequence is 3, not {}.".format(str(fib(4))))
        self.assertEqual(fib(5),5,"The fifth element of the Fibonnaci sequence is 5, not {}.".format(str(fib(5))))
        #self.assertRaises(f(-1)
    def test_init(self):
        self.c=cached(fib,1)
        self.assertEqual(len(self.c.c),0,"The cache was malformed.")
        self.assertEqual(self.c.n,1,"The cache max size was not recorded properly.")
        self.assertEqual(self.c.f(0),fib(0),"The function was not entered correctly.")
    def test_cache(self):
        self.c=cached(fib,1)
        i=self.c(0)
        self.assertEqual(len(self.c.c),1,"The value was not cached properly.")
        self.assertEqual(self.c(0),i,"The cached answer was incorrect.")
    def test_pop(self):
        global fib
        self.c=cached(fib,3)
        del fib
        fib=self.c
        i=fib(3)
        self.assertEqual(len(self.c.c),3,"Recursion not properly set up for caching.")
        i=fib(4)
        self.assertEqual(len(self.c.c),3,"Maximum cache size not implemented correctly.")
    def test_speed(self):
        global fib
        t1=None
        t2=None
        with Timer() as t1:
            k=fib(32)
        self.c=cached(fib,-1)
        del fib
        fib=self.c
        with Timer() as t2:
            k=fib(32)
        self.assertLess(t2.interval,t1.interval,"There isn't a speed up... This is useless then, I suppose.")
        with Timer() as t1:
            k=fib(32)
        self.assertGreater(t2.interval,t1.interval,"There isn't a speed up... This is useless then, I suppose.")
        
def gcd(a,b):
    def GCD(a,b):
        r=a%b
        if r==0:
            return b
        else:
            return gcd(b,r)
    c=cached(GCD,10000)
    del GCD
    global gcd
    gcd=c
    return gcd(a,b)
        
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

# def alphaBetaAskF(board,maxdepth,nextstateGeneratorFunction,heuristic,boardcheck,flipPlayers):
    # "This returns the alphabeta calculated best next board state."
    # # I will take advantage of the fact that the heuristic for max is equal to the negative of the heuristic for min (or alpha and beta respectively) to simplify this to have both "characters" "thinking" they are alpha.
    # # Pseudo-code from Wikipedia used as a basis.
    # alpha=[-float('Inf'),[]]
    # for child in nextstateGeneratorFunction(board):
        # nalpha = -alphabeta(flipPlayers(child), maxdepth-1, -float('Inf'), float('Inf') ,nextstateGeneratorFunction, heuristic, boardcheck, flipPlayers)
        # if alpha[0]<nalpha:
            # alpha[0]=nalpha
            # alpha[1]=child
    # return alpha[1]
# def alphabetaF(board,depth,alpha,beta,nextstateGeneratorFunction,heuristic,boardcheck, flipPlayers):
    # "This returns the alphabeta calculated best next board value."
    # # I will take advantage of the fact that the heuristic for max is equal to the negative of the heuristic for min (or alpha and beta respectively) to simplify this to have both "characters" "thinking" they are alpha.
    # # Pseudo-code from Wikipedia used as a basis.
    # if  depth == 0:
        # return heuristic(board)
    # check=boardcheck(board)
    # if check==1: #WIN
        # return float('Inf')
    # if check==-1: #LOSE
        # return -float('Inf')
    # if check==-2: #CATSGAME
        # return 0
    # for child in nextstateGeneratorFunction(board):
        # alpha = max(alpha, -alphabeta(flipPlayers(child), depth-1, -beta, -alpha ,nextstateGeneratorFunction, heuristic, boardcheck, flipPlayers))     
        # if beta < alpha:
            # break #Beta cut-off
    # return alpha
# alphaBetaC=cached(alphaBetaF,-1)
# alphaBeta=alphaBetaC
# alphaBetaAskC=cached(alphaBetaAskF,-1)
# alphaBetaAsk=alphaBetaC

if __name__ == '__main__':
    ut.main()
