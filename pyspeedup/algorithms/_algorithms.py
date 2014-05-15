from pyspeedup import concurrent

@concurrent.Cache
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

def powersInMod(n):
    return set((x*x)%n for x in range(0,n//2+1))

def isSquare(n):
    '''Checks for perfect squares by checking mod 64 to rule out 52/64 cases immediately.'''
    if n%isSquare.mod in isSquare.set:
        m=math.floor(math.sqrt(n))
        return m*m==n
    return False
isSquare.mod=64 #This and the below can be changed if a different value is deemed better.
isSquare.set=powersInMod(isSquare.mod) #The set of all perfect squares mod the above number.

@cached(10000)
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
        t=factor(a-b)
        for i in factor(a+b):
            t.append(i)
        return list(sorted(t))

def certificateOfPrimitivity(number,modulo):
    '''Generates a set of the distinct prime factors, and their least nonnegative residues of the given number in the given modulo.'''
    DIV=set(factor(modulo-1))
    RES=[]
    for i in DIV:
        RES.append(int(number**((modulo-1)/i)%modulo))
    return DIV,RES

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

def findLowestPseudoprime(bases=(2,)):
    n=3
    try:
        for i in bases:
            pass
    except:
        bases=(bases,) #Makes it iterable.
    while(1):
        n+=1
        next=False
        for i in bases:
            if not StrongPrimeTest(n,i):
                next=True
                break
        if not next and not isPrime(n):
            return n

def FermatPrimeTest(n,t=2):
    '''Tests for primitivity using Fermat's Primitivity Test. Does not guarantee primitivity.'''
    return pow(t,n-1,n)==1

CT51=[12433,11524,7243,7459,14303,6127,10964,16399,9792,13629,14407,18817,18830,13556,3159,16647,5300,13951,81,8986,8007,13167,10022,17213,2264,961,17459,4101,2999,14569,17183,15827]
CT52=[6340,8309,14010,8936,27358,25023,16481,25809,23614,7135,24996,30590,27570,26486,30388,9395,27584,14999,4517,12146,29421,26439,1606,17881]

class RSAKey:
    def __init__(self,n,e):
        self.n=n
        self.e=e
    def encrypt(self,array):
        out=[]
        try:
            for i in array:
                break
        except:
            array=(array,)
        for i in array:
            out.append(pow(i,self.e,self.n))
        return out
    def decrypt(self,array):
        self.decrypt=self.encrypt
        return self.encrypt(array)


class RSAPrivateKey(RSAKey):
    pass

class RSAPublicKey(RSAKey):
    pass

class RSAMaster:
    def __init__(self,p,q):
        self.p=p
        self.q=q
        self.n=p*q
        self.phi=(p-1)*(q-1)
        self.e=random.randint(1,self.phi)
        while gcd(self.e,self.phi)!=1:
            self.e=(self.e+1)%self.phi
        self.d=invMod(self.e,self.phi)
        self.public=RSAPublicKey(self.n,self.e)
        self.private=RSAPrivateKey(self.n,self.d)

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

def cycleCheck(N):
    def f(x):
        return (x*x)%N
    x=2
    y=f(2)
    c=0
    while x!=y:
        x=f(x)
        y=f(f(y))
        c+=1
    return c

import math, operator
def Shanks(n,alpha,beta,displayLists=False):
    '''Uses the Shanks algorithm to solve the discrete log problem for log_alpha(beta) in mod n.'''
    m=int(math.ceil(math.sqrt(n)))
    invAlpha=invMod(alpha,n)
    alphaM=pow(alpha,m,n)
    L1=[(0,1)]
    L2=[(0,beta)]
    for j in range(1,m-1):
        #(j,alpha**(m*j)%n)
        L1.append((j,(L1[j-1][1]*alphaM)%n))
        #(i,beta*alpha**(-i)%n)
        L2.append((j,(L2[j-1][1]*invAlpha)%n))
    L1.sort(key=operator.itemgetter(1))
    L2.sort(key=operator.itemgetter(1))
    if displayLists:
        print(L1)
        print(L2)
    try:
        j=0
        i=0
        while L1[j][1]!=L2[i][1]:
            if L1[j][1]>L2[i][1]:
                i+=1
            else:
                j+=1
        return (m*L1[j][0]+L2[i][0])%n
    except: #If it exceeds the index, there was no match, and thus...
        raise Exception("No solution.")

class ElGamal:
    '''A very basic ElGamal implementation.'''
    def __init__(self,p,alpha,a,beta):
        self.p=p
        self.alpha=alpha
        self.a=a
        self.beta=beta
    def decrypt(self,y1,y2):
        '''Decrypt in the established ElGamal cryptosystem.'''
        #y2(y1**a)**-1 mod p
        return y2*invMod(pow(y1,self.a,self.p),self.p)%self.p

def decode(array):
    out=""
    for i in array:
        a=i%26
        i//=26
        out+=chr(ord('A')+i//26)+chr(ord('A')+i%26)+chr(ord('A')+a)
    return out

eG=ElGamal(31847,5,7899,18074)

c=[(3781,14409), (31552,3930), (27214,15442), (5809,30274), (5400,31486), (19936,721), (27765,29284), (29820,7710), (31590,26470), (3781,14409), (15898,30844), (19048,12914), (16160,3129), (301,17252), (24689,7776), (28856,15720), (30555,24611), (20501,2922), (13659,5015), (5740,31233), (1616,14170), (4294,2307), (2320,29174), (3036,20132), (14130,22010), (25910,19663), (19557,10145), (18899,27609), (26004,25056), (5400,31486), (9526,3019), (12962,15189), (29538,5408), (3149,7400), (9396,3058), (27149,20535), (1777,8737), (26117,14251), (7129,18195), (25302,10248), (23258,3468), (26052,20545), (21958,5713), (346,31194), (8836,25898), (8794,17358), (1777,8737), (25038,12483), (10422,5552), (1777,8737), (3780,16360), (11685,133), (25115,10840), (14130,22010), (16081,16414), (28580,20845), (23418,22058), (24139,9580), (173,17075), (2016,18131), (19886,22344), (21600,25505), (27119,19921), (23312,16906), (21563,7891), (28250,21321), (28327,19237), (15313,28649), (24271,8480), (26592,25457), (9660,7939), (10267,20623), (30499,14423), (5839,24179), (12846,6598), (9284,27858), (24875,17641), (1777,8737), (18825,19671), (31306,11929), (3576,4630), (26664,27572), (27011,29164), (22763,8992), (3149,7400), (8951,29435), (2059,3977), (16258,30341), (21541,19004), (5865,29526), (10536,6941), (1777,8737), (17561,11884), (2209,6107), (10422,5552), (19371,21005), (26521,5803), (14884,14280), (4328,8635), (28250,21321), (28327,19237), (15313,28649)]
m=[]
for i in c:
    m.append(eG.decrypt(i[0],i[1]))
decode(m)

#def abundant(n):
    #if n<12:
        #return False
    #f=factor(n)
    #m=1
    #for x in set(f):
        #c=f.count(x)
        #m*=(x**(c+1)-1)/(x-1)
    #return m>2*n
#
#L=[]
#for i in range(28123):
    #if abundant(i):
        #L.append(i)
#
#s=0
#for i in range(28123):
    #j=0
    #add=True
    #while L[j]+L[0]<i and j<len(L)-1:
        #j+=1
    #for k in L:
        #while j>0 and L[j]+k>i:
            #j-=1
        #if L[j]+k>i:
            #break
        #if L[j]+k==i:
            #add=False
            #break
    #if add==True:
        #s+=i

#i=1
#n=4
#while n>0:
#    a,b=certificateOfPrimitivity(i,5881)
#    if not 1 in b:
#        print i,b
#        n-=1
#    i+=1