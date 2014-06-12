from pyspeedup import concurrent
import math
from pyspeedup.algorithms import isSquare

@concurrent.Cache
def factor(N):
    '''Utilizes Fermat's sieve and recursive caching to reduce factorization time, mostly in repeated factorization.'''
    if N<0:
        t=factor(-N)
        t.insert(0,-1)
        return t #Works on positive and negative integers
    if N<4:
        return [N] #Positive integers under 4 are factored already (ignoring 1)
    if N%2==0:
        t=factor(N//2)
        t.insert(0,2)
        return t
    a = int(math.ceil(math.sqrt(N)))
    b2 = a*a - N
    while not isSquare(b2):
        b2+=a+a+1
        a += 1    # equivalently: a+=1; b2 = a*a - N
    b=int(math.floor(math.sqrt(b2)))
    assert b*b==b2
    if a-b==1:
        return [a+b]
    else:
        factor.apply_async(a-b)
        factor.apply_async(a+b)
        t=factor(a-b)
        for i in factor(a+b):
            t.append(i)
        return list(sorted(t))