def divideMod(numerator,denominator,modulo):
    '''Uses the extended Euclidean algorithm to find a modular quotient.'''
    quotients=[] #Stores the quotients for use in constructing the inverse.
    (q,r)=divmod(modulo,denominator) #Python native function that performs Euclidean division.
    dividend,denominator=denominator,r #Python syntax for quick value reassignment, which allows for swapping without a temporary variable.
    while r!=0:
        quotients.append(q)
        (q,r)=divmod(dividend,denominator)
        dividend,denominator=denominator,r
    if numerator%dividend!=0: #Then the does not divide the numerator, and thus...
        raise Exception("There is no solution in the integers mod {0}.".format(modulo))
    prev,solution=0,numerator/dividend #Set the tabular initial values.
    while len(quotients)>0: #traverse the list backwards to construct the inverse.
        prev,solution=-solution,-(prev+quotients.pop()*solution) #Negatives account for sign change in algorithm lazily.
    return solution%modulo