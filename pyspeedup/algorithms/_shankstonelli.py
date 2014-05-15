from pyspeedup.algorithms import jacobi_symbol

def tsSquareRoot(a,p):
    '''Calculates the square root mod p of a.'''
    jacobi=jacobi_symbol(a,p)
    if jacobi==-1:
        raise ValueError("No square root mod {0} exists.".format(p))
    s=p-1
    e=0
    while s%2==0: #Find p-1=s*2^e with odd s.
        e+=1
        s//=2
    n=2
    while jacobi_symbol(n,p)!=-1:
        n+=1 #Find an n s.t. (n/p)==-1
    x=pow(a,((s+1)/2),p) #first guess
    b=pow(a,s,p) #first guess correction
    g=pow(n,s,p) #quantity to modify x and b
    r=e
    while r>0:
        #ord_p(g)=ord_p(pow(n,s,p))
        #Note (n^s)^2^e=n^(2^e*s)=n^(p-1)=1 mod p
        #claim ord_p(g)=2^e, because
        #(n^s)^2^(e-1)=n^(s*2^e)/2=n^((p-1)/2)=jacobi_symbol=-1
        #Find m s.t. 0<=m<r and b^(2^m)==1
        m=0
        bp=b
        while m<r:
            if bp==1:
                break
            bp=(bp*bp)%p
            m+=1
        if m==0:
            break
        #Having found m, we update:
        g=pow(g,pow(2,(r-m-1),p),p)
        x=(x*g)%p
        g=(g*g)%p
        b=(b*g)%p
        r=m
    return x
