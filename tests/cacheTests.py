import unittest as ut

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

    #TODO: Test the concurrent cache.