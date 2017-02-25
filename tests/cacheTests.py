import unittest as ut
from pyspeedup.algorithms import cached
from pyspeedup._utils._timer import Timer
from pyspeedup.concurrent import Cache
from pyspeedup.concurrent import buffer
#from Process import freeze_support

def uncachedFib(a):
    if a in [0,1]:
        return a
    if a<0:
        raise Exception("Reverse fibonacci sequence not implemented.")
    return uncachedFib(a-1)+uncachedFib(a-2)

class fibTest(ut.TestCase):
    def test_fib(self):
        self.assertEqual(uncachedFib(0),0,"The zeroth element of the Fibonnaci sequence is 0, not {}.".format(str(uncachedFib(0))))
        self.assertEqual(uncachedFib(1),1,"The first element of the Fibonnaci sequence is 1, not {}.".format(str(uncachedFib(1))))
        self.assertEqual(uncachedFib(2),1,"The second element of the Fibonnaci sequence is 1, not {}.".format(str(uncachedFib(2))))
        self.assertEqual(uncachedFib(3),2,"The third element of the Fibonnaci sequence is 2, not {}.".format(str(uncachedFib(3))))
        self.assertEqual(uncachedFib(4),3,"The fourth element of the Fibonnaci sequence is 3, not {}.".format(str(uncachedFib(4))))
        self.assertEqual(uncachedFib(5),5,"The fifth element of the Fibonnaci sequence is 5, not {}.".format(str(uncachedFib(5))))

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
        _=self.c(3)
        self.assertEqual(len(self.c.c),3,"Recursion not properly set up for caching.")
        _=self.c(4)
        self.assertEqual(len(self.c.c),3,"Maximum cache size not implemented correctly.")
    def test_speed(self):
        with Timer() as t1:
            _=uncachedFib(32)
        self.c.n=-1
        with Timer() as t2:
            _=self.c(32)
        self.assertLess(t2.interval,t1.interval,"There isn't a speed up... This is useless then, I suppose.")
        with Timer() as t1:
            _=self.c(32)
        self.assertGreater(t2.interval,t1.interval,"There isn't a speed up... This is useless then, I suppose.")


def fib(a): #Needs to be in the global scope.
    if a in [0,1]:
        return a
    if a<0:
        raise Exception("Reverse fibonacci sequence not implemented.")
    fib.apply_async(a-1) #Also needs to prepare multiprocessed branching.
    fib.apply_async(a-2)
    return fib(a-1)+fib(a-2)

class CacheTest(ut.TestCase):
    c=None
    def setUp(self):
        fib=Cache(globals()['fib'])
        self.c=fib
    def test_fib(self):
        self.assertEqual(self.c(0),0,"The zeroth element of the Fibonnaci sequence is 0, not {}.".format(str(self.c(0))))
        self.assertEqual(self.c(1),1,"The first element of the Fibonnaci sequence is 1, not {}.".format(str(self.c(1))))
        self.assertEqual(self.c(2),1,"The second element of the Fibonnaci sequence is 1, not {}.".format(str(self.c(2))))
        self.assertEqual(self.c(3),2,"The third element of the Fibonnaci sequence is 2, not {}.".format(str(self.c(3))))
        self.assertEqual(self.c(4),3,"The fourth element of the Fibonnaci sequence is 3, not {}.".format(str(self.c(4))))
        self.assertEqual(self.c(5),5,"The fifth element of the Fibonnaci sequence is 5, not {}.".format(str(self.c(5))))
    def test_cache(self):
        i=self.c(0)
        self.assertEqual(len(self.c._d),1,"The value was not cached properly.")
        self.assertEqual(self.c(0),i,"The cached answer was incorrect.")
    def test_speed(self):
        with Timer() as t1:
            _=uncachedFib(32)
        with Timer() as t2:
            _=self.c(32)
        #This test needs multiple cores to get a speed up, by nature.
        #self.assertLess(t2.interval,t1.interval,"There isn't a speed up... This is useless then, I suppose.")
        with Timer() as t1:
            _=self.c(32)
        self.assertGreater(t2.interval,t1.interval,"There isn't a speed up... This is useless then, I suppose.")
#     def test_completion(self):
#         self.assertEqual(_func(7,7,3),17,"_func(7,7,3) is 17 not {}".format(_func(7,7,3)))
#         self.assertEqual(_func(50,50,3),16475640049,"_func(50,50,3) is 16475640049 not {}".format(_func(50,50,3)))

@Cache
def _func(size,mx,mn):
    '''A test function.'''
    if size<mn or mx<mn:
        return 1 #Empty
    if size<mx:
        return _func(size,size,mn)
    count=_func(size,mx-1,mn)
    if mx==size:
        return count+1
    for i,j in enumerate(range(size-mx,-1,-1)):
        _func.apply_async(i-1,mx-1,mn)
        _func.apply_async(j-1,mx,mn)
    for i,j in enumerate(range(size-mx,-1,-1)):
        count+= _func(i-1,mx-1,mn) * _func(j-1,mx,mn)
    return count

class bufferTest(ut.TestCase):
    def setUp(self):
        self.primes=postponed_sieve()
        self.mPrimes=concurrent_sieve
        self.cPrimes=concurrent_sieve()
    def test_primes(self):
        p=[2,3,5,7,11,13,17,19,23,29,31,37,41,43]
        for i in p:
            self.assertEqual(next(self.primes),i,"The generator skipped {}.".format(i))
    def test_mPrimes(self):
        for i in range(100):
            self.assertEqual(next(self.primes),self.mPrimes[i],"The buffer skipped prime number {}.".format(i))
    def test_cPrimes(self):
        for i in range(100):
            p=next(self.primes)
            self.assertEqual(p,self.mPrimes[i],"The buffer skipped prime number {}.".format(i))
            self.assertEqual(p,next(self.cPrimes),"The buffered generator skipped prime number {}.".format(i))
    def test_cache(self):
        for i in range(100):
            self.assertEqual(self.mPrimes[i],self.mPrimes._cache[i],"The value was not cached properly.")

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

def concurrent_sieve():                  # postponed sieve, by Will Ness
    yield 2; yield 3; yield 5; yield 7;  # original code David Eppstein,
    D = {}                               #            ActiveState Recipe 2002
    ps = (p for p in concurrent_sieve())  # a separate Primes Supply:
    p = next(ps) and next(ps)            # (3) a Prime to add to dict
    q = p*p                              # (9) when its square is
    c = 9                                # the next Candidate
    while True:
        if c not in D:                   # not a multiple of any prime seen so far:
            if c < q: yield c            #   a prime, or
            else:                        #   (c==q) next prime's square:
                s = 2 * p                #     (9+6,6 : 15,21,27,33,...)
                x = c + s                # make no multiple keys in Dict
                while x in D: x += s     # increment by the given step
                D[x] = s
                p=next(ps)               #     (5)
                q=p*p                    #     (25)
        else:                            # a composite:
            s = D.pop(c)                 #   step of increment
            x = c + s                    # make no multiple keys in Dict
            while x in D: x += s         # increment by the given step
            D[x] = s                     #   next multiple, same step
        c += 2                           # next odd candidate
concurrent_sieve=buffer()(concurrent_sieve)

def add(D,x,s):                          # make no multiple keys in Dict
    while x in D: x += s                 # increment by the given step
    D[x] = s

if __name__=='__main__':
    freeze_support()
    ut.main()
