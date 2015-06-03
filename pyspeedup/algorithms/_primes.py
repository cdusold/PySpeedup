import random
import math
from pyspeedup.algorithms import gcd, factor

def FermatPrimeTest(n,t=2):
    '''Tests for primitivity using Fermat's Primitivity Test. Does not guarantee primitivity.'''
    return pow(t,n-1,n)==1

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

def BrutePrimitivityTest(n):
    '''Uses simple brute force calculation to determine primitivity.'''
    for i in range(2,int(math.sqrt(n)+1)):
        if n%i==0:
            return False
    return True

def BailliePSWPrimalityTest(n):
    #TODO: Fix http://en.wikipedia.org/wiki/Baillie-PSW_primality_test
    if n>BailliePSWPrimalityTest.knownupperbound:
        raise Exception("Not dealing with probable primes yet.")
    return StrongPrimeTest(n) and LucasProbablePrime(n)
BailliePSWPrimalityTest.knownupperbound=2**64

def LucasProbablePrime(n):
    pass #TODO! http://en.wikipedia.org/wiki/Lucas_pseudoprime


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

def certificateOfPrimitivity(number,modulo):
    '''Generates a set of the distinct prime factors, and their least nonnegative residues of the given number in the given modulo.'''
    DIV=set(factor(modulo-1))
    RES=[]
    for i in DIV:
        RES.append(int(number**((modulo-1)/i)%modulo))
    return DIV,RES

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

def findCertificateOfPrimitivity(p):
    i=1
    b=[1]
    while 1 in b:
        i+=1
        a,b=certificateOfPrimitivity(i,p)
    return a,b
    