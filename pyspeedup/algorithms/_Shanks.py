import math, operator
from pyspeedup.algorithms import invMod

def Shanks(n,alpha,beta):
    '''Uses the Shanks algorithm to solve the discrete log problem for log_alpha(beta) in mod n.'''
    m=int(math.ceil(math.sqrt(n)))
    #The multiplicative difference between elements in list 1 is alpha to the mth power.
    alphaM=pow(alpha,m,n)
    #The multiplicative difference between elements in list 2 is the inverse of alpha.
    invAlpha=invMod(alpha,n)
    L1=[(0,1)]
    L2=[(0,beta)]
    for j in range(1,m-1):
        #(j,alpha**(m*j)%n)
        L1.append((j,(L1[j-1][1]*alphaM)%n))
        #(i,beta*alpha**(-i)%n)
        L2.append((j,(L2[j-1][1]*invAlpha)%n))
    L1.sort(key=operator.itemgetter(1))
    L2.sort(key=operator.itemgetter(1))
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
