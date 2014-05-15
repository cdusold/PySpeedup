import random as rnd
import copy

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