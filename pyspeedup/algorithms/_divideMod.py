from pyspeedup import concurrent

def divideMod(numerator,denominator,modulo):
    '''Uses the extended Euclidean algorithm to find a modular quotient.'''
    #Since the quotient values are used in reverse order, postfix recursion makes sense for this equation.
    # The following recursively uses Euclidean divison, then applies the tabular algorithm upon returning.
    _,solution=_dM(numerator,denominator,modulo)
    return solution%modulo

@concurrent.Cache
def _dM(numerator,denominator,modulo):
    '''A recursive helper function for use in dividing.'''
    (q,r)=divmod(modulo,denominator) #Python native function that performs Euclidean division.
    if r==0:
        if numerator%denominator!=0: #Then the does not divide the numerator, and thus...
            raise Exception("There is no solution in the given set of integers.")
        return (0,numerator//denominator)
    prev,solution=_dM(numerator,r,denominator)
    #Python syntax for quick value reassignment, which allows for swapping without a temporary variable.
    prev,solution=-solution,-(prev+q*solution) #Negatives account for sign change in algorithm lazily.
    return prev,solution