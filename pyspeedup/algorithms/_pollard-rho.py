def DiscreteLog(p,n,alpha,beta):
    '''Solves the discrete log problem using the Pollard Rho algorithm.'''
    def f(x,a,b):
        temp=x%3
        #Using sets directly from Example 6.3,
        #S1={x in integers mod p: x equivalent to 1 mod 3}
        #S2={x in integers mod p: x equivalent to 0 mod 3}
        #S3={x in integers mod p: x equivalent to 2 mod 3}
        if temp==1:
            return (beta*x)%p,a,(b+1)%n
        if temp==0:
            return (x*x)%p,(2*a)%n,(2*b)%n
        return (alpha*x)%p,(a+1)%n,b
    x,a,b=f(1,0,0)
    xp,ap,bp=f(x,a,b)
    while x!=xp:
        x,a,b=f(x,a,b)
        xp,ap,bp=f(xp,ap,bp)
        xp,ap,bp=f(xp,ap,bp)
    if gcd((bp-b)%n,n)!=1:
        raise Exception("Failed to determine the discrete log.")
    return((a-ap)*invMod((bp-b)%n,n))%n