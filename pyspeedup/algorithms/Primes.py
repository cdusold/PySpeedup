"""
A module designed to act as a singleton-like prime suite.

Once imported, it begins processes designed to help determine what numbers are prime
and uses concurrent branching to split primality tests and prime factorizations and
speed up the whole process.
"""
import cPickle
from os.path import join
from threading import Thread
from time import sleep
import atexit
from pyspeedup.memory import OrderedDiskDict, DiskDict

D = DiskDict()
F = OrderedDiskDict()
c = 3
p = 3
q = 9
thread = None
file_location = None

def load_primes(location):
    """
    In order to not repeat computation, states and lists
    need to be saved between runs. This function links a
    location to the computations performed to keep results
    indefinitely.
    """
    global D
    global F
    global c
    global p
    global file_location
    stop_seive()
    del D
    D = DiskDict() #New seive object.
    D.link_to_disk("seive",file_location=location, size_limit = 65536, max_pages = 32) #Load or create persistance.
    del F
    F = OrderedDiskDict() #A new factor list object.
    F.link_to_disk("factors",file_location=location, size_limit = 65536, max_pages = 32) #Load or create persistance.
    try:
        with open(D._file_base+"current",'rb') as f:
            c,p = cPickle.load(f)
    except:
        c,p = 3,3
    file_location = location

def start_seive():
    global thread
    if thread == None:
        thread = Thread(target = _prime_seive)
        thread.start()

def stop_seive():
    global stop
    global thread
    if thread:
        stop = True
        thread.join()
    thread = None
atexit.register(stop_seive)

def _prime_seive():
    """
    A persistant seive designed to run in the background.
    WARNING: This is continuously use up memory until it
    runs out, at about a rate of x/ln(x-1).
    """
    global stop
    global D
    global F
    global c
    global p
    global file_location
    stop = False
    if 2 not in F:
        F[2] = 2
    q = p * p
    while stop == False:
        if c not in D:
            if c < q:
                F[c] = c #New prime
            else:
                F[c] = [p,p] #Reached a square of the current sliding prime.
                s = 2 * p #Skip even numbers in dict.
                x = c + s #Jump to the next non-even multiple of p.
                while x in D: x += s #Continue jumping until it's unique.
                D[x] = p #Then add that multiple to the dict.
                p = nextPrime(p) #Get the next sliding prime.
                q = p * p #And wait until the square is seen to add it to the seive.
        else:
            p1 = D.pop(c) #We reached a multiple of p1.
            F[c] = [p1, c//p1] #Add it to the factor list.
            s = 2 * p1 #Skip even numbers in dict.
            x = c + s #And find the next odd multiple.
            while x in D: x += s #Make it unique.
            D[x] = p1 #And put it back in the seive.
        c += 2 #We skip all even numbers since 2 is hard coded.
        sleep(0)
    with open(D._file_base+"current",'wb') as f:
        cPickle.dump((c,p), f)

def nextPrime(p):
    """
    Returns the next prime after 'p'.
    """
    p = round(p)
    if p<2:
        return 2
    if p%2 == 0:
        p-=1
    p+=2
    while not is_prime(p):
        p+=2
    return p

def factor(N):
    """
    Set up a bunch of factorization routines in parallel if
    the factors of N are not known. Once one finds two factors,
    stop all the rest of them and return. If one of the algorithms
    tell us that N is prime, return N.

    This function ignores any algorithms that return "probably prime."
    """
    global F
    if N in F:
        return F[N]
    if N<-1:
        return [-1,abs(N)]
    if N<3:
        return N
    if N%2==0: #This reduces the factorization diskdict significantly, and gets half of all values.
        return [2,N//2]
    #TODO: Replace with multiprocess structure, starting with trial division.
    #TODO: Add BailliePSW and/or one of its submethods after trial division.
    found = fermat_factorization(N)
    F[N] = found
    return found

def fermat_factorization(N):
    """
    Fermat's factorization algorithm. Takes N and returns two
    of its factors.

    Reference: http://en.wikipedia.org/wiki/Fermat's_factorization_method
    """
    import math
    if N<-1:
        return [-1,N]
    if N<3:
        return N
    if N%2==0:
        return [2,N//2]
    a = math.ceil(math.sqrt(N))
    b2 = a*a - N
    b=math.floor(math.sqrt(b2))
    while b*b!=b2: #TODO: replace with an efficient isSquare algo.
        b2 += a + a + 1    # equivalently: a = a + 1
        a += 1 #                           b2 = a*a - N
        b=math.floor(math.sqrt(b2)) #TODO, only do on success.
    if a-b==1:
        return N
    return [a-b,a+b]

def is_prime(N):
    """
    Uses the cached factorization list to retrieve
    whether N is prime (in O(1)) or Fermat's
    factorization method to figure it out (in O(n)).
    """
    global F
    if N < 2:
        return False
    if N in F:
        return F[N]==N
    return factor(N)==N

#TODO: cached or not?
def get_factorization(q):
    """
    Gets the factorization of q either through looking
    up precomputed values (in O(ln(q)) or O(ln(ln(q)))
    after tree balancing) or by running Fermat's
    factorization method (in O(n ln(n))).
    """
    global F
    t=[]
    if q in F:
        t = F[q]
    else:
        t = factor(q)
    if t != q:
        m = []
        for i in t:
            m.extend(get_factorization(i))
        t = m
    else:
        t = [t]
    return t

if __name__ == "__main__":
    from os.path import expanduser
    load_primes("D:/.pyspeedup")
    start_seive()
    while len(F)<1000000: 
        sleep(1)
    stop_seive()
    print(c)
    print(p)
    print(F[9])
    print(F[7])
    print(get_factorization(100))
    print(F[205])
    print(get_factorization(9999999))
