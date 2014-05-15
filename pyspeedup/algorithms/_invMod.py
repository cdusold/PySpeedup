from pyspeedup import concurrent

def invMod(number,modulo):
    '''Uses the extended Euclidean algorithm to deduce the inverse of 'number' mod 'modulo'.'''
    #Since the quotient values are used in reverse order, postfix recursion makes sense for this equation.
    # The following recursively uses Euclidean divison, then applies the tabular algorithm upon returning.
    _,solution=_iM(modulo,number)
    return solution%modulo

@concurrent.Cache
def _iM(dividend,divisor):
    '''A recursive helper function for use in inverting.'''
    (q,r)=divmod(dividend,divisor) #Python native function that performs Euclidean division.
    if r==0:
        if divisor!=1:
            raise Exception("Number not invertible in given set of integers.")
        return (0,1)
    prev,solution=_iM(divisor,r)
    #Python syntax for quick value reassignment, which allows for swapping without a temporary variable.
    prev,solution=-solution,-(prev+q*solution) #Negatives account for sign change in algorithm lazily.
    return prev,solution