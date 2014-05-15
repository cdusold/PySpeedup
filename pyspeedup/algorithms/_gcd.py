from pyspeedup import concurrent

@concurrent.Cache
def gcd(a,b):
    '''Using the extended Euclidean algorithm, finds the gcd between a and b.'''
    r=a%b
    if r==0:
        return b
    else:
        return gcd(b,r)