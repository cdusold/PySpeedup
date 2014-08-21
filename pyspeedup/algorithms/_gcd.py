from pyspeedup import concurrent

@concurrent.Cache
def gcd(a,b):
    '''Using the extended Euclidean algorithm, finds the gcd between a and b.

    For example::

        >>> gcd(5,10)
        5
        >>> gcd(1024,768)
        256
        >>> gcd(1474038573,183508437983)
        1

    '''
    r=a%b
    if r==0:
        return b
    else:
        return gcd(b,r)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
