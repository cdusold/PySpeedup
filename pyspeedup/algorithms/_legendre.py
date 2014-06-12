from pyspeedup import concurrent

@concurrent.Cache
def jacobi_symbol(a, n):
    """Calculate the Jacobi symbol (a/n), which is equivalent to the Legendre for prime n."""
    if n%2==0:
        raise ValueError("The Jacobi symbol is undefined for even n.")
    if a<0 or a>=n:
        a%=n #If a equiv b mod n, (a/n)=(b/n)
    if a == 0:
        return 0 #For a divisible by n, (a/n)=0 by definition.
    elif a == 1:
        return 1 #For a equiv 1 mod n, 1**2 equiv a.
    elif a == 2: #a equiv 2 mod n has a proven solution for all (2/n).
        if n % 8 in [3, 5]:
            return -1
        elif n % 8 in [1, 7]:
            return 1
    elif a < 0:
        return (-1)**((n-1)/2) * jacobi_symbol(-1*a, n)

    if a % 2 == 0: #(a*b/n)=(a/n)*(b/n)
        jacobi_symbol.apply_async(2, n)
        jacobi_symbol.apply_async(a/2, n)
        return jacobi_symbol(2, n) * jacobi_symbol(a / 2, n)
    else: #Using the law of quadratic reciprocity:
        if a % 4 == n % 4 == 3:
            return -1 * jacobi_symbol(n, a)
        else:
            return jacobi_symbol(n, a)