import numbers
#import itertools #For iter.
import functools
import operator
import math
from algorithms import factor

def product(xs):
    return functools.reduce(operator.mul, xs, 1)
class Fraction(numbers.Rational): #TODO Update into FactoredFraction or FactoredRational and iron out Int only support.
    def __init__(self,*args):
        self._d={}
        if not args:
            pass
        elif len(args)==1:
            if args[0]==0:
                self[0]=1
            elif isinstance(args[0],FactoredFraction):
                self._d={k:v for k,v in args[0]._d.viewitems() if type(k)==int and type(v)==int}
                if len(self)!=len(args[0]):
                    raise NotImplementedError()
            elif type(args[0])==dict:
                self._d={k:v for k,v in args[0].viewitems() if type(k)==int and type(v)==int}
            elif isinstance(args[0],numbers.Integral):
                f=factor(abs(int(args[0])))
                if args[0]<0:
                    f.append(-1)
                for i in set(f):
                    self._d[i]=f.count(i)
            elif isinstance(args[0],numbers.Rational):
                n=factor(abs(args[0].numerator))
                d=factor(abs(args[0].denominator))
                if args[0]<0:
                    f.append(-1)
                nu=set(n)
                de=set(d)
                for i in nu&de:
                    self[i]=n.count(i)-d.count(i)
                for i in nu-de:
                    self[i]=n.count(i)
                for i in de-nu:
                    self[i]=-d.count(i)
            else:
                raise NotImplementedError()
        else: #TODO This is exploitable...
            for i in set(args):
                if not isinstance(i,int):
                    raise NotImplementedError()
                self[i]=args.count(i)
    def __iter__(self):
        '''TODO: This would be useful to iterate through primes.'''
        raise NotImplementedError()
    def __next__(self):
        '''TODO: Needs to be implemented with the above.'''
        raise NotImplementedError()
    def __reversed__(self):
        '''TODO: Probably not important. Implement if needed.'''
        raise NotImplementedError()
    def __getitem__(self,key):
        if not isinstance(key,numbers.Integral):
            raise TypeError()
        return self._d.get(key,0)
    def __setitem__(self,key,value):
        if not isinstance(key,numbers.Integral) or not isinstance(value,numbers.Integral):
            raise TypeError()
        if value==0:
            del self[key]
        elif key==0:
            for i in list(self._d):
                del self._d[i]
            self._d[0]=1
        elif key==-1:
            if value%2==0:
                del self[-1]
            else:
                self[-1]=1
        elif key<0:
            self._d[-1]+=value
            self._d[abs(key)]=value
        else:
            self._d[key]=value
    def __delitem__(self,key):
        if key not in self:
            return
        else:
            del self._d[key]
    @property
    def numerator(self):
        return product([k**v for k,v in self._d.items() if v>0])
    @property
    def denominator(self):
        return product([k**v for k,v in self._d.items() if v<0])
    def fraction(self):
        return fractions.Fraction(self.numerator,self.denominator)
    def gcd(self,other): #Forces self/gcd and other/gcd to be integer valued.
        if isinstance(other,FactoredFraction):
            t=other
        elif isinstance(other,numbers.Rational):
            t=FactoredFraction(other)
        else:
            raise NotImplementedError()
        return FactoredFraction({k:min(self[k],t[k]) for k in self._d.keys()|t._d.keys()})
    def __int__(self):
        return int(product([k**self._d[k] for k in self._d.keys()]))
    def __float__(self):
        return float(product([k**self._d[k] for k in self._d.keys()]))
    def __eq__(self,other):
        if isinstance(other,FactoredFraction):
            return all(self[i]==other[i] for i in self._d.keys()|other._d.keys())
        if isinstance(other,numbers.Rational):
            return self.fraction()==other
        else:
            return float(self)==other
    def __ne__(self,other):
        if isinstance(other,FactoredFraction):
            return any(self[i]!=other[i] for i in self._d.keys()|other._d.keys())
        if isinstance(other,numbers.Rational):
            return self.fraction()!=other
        else:
            return float(self)!=other
    def __lt__(self,other):
        if isinstance(other,numbers.Integral):
            return self.numerator<int(other)*self.denominator
        if isinstance(other,numbers.Rational):
            return self.numerator*other.denominator<other.numerator*self.denominator
        return float(self)<other
    def __gt__(self,other):
        if isinstance(other,numbers.Integral):
            return self.numerator>int(other)*self.denominator
        if isinstance(other,numbers.Rational):
            return self.numerator*other.denominator>other.numerator*self.denominator
        return float(self)>other
    def __le__(self,other):
        if isinstance(other,numbers.Integral):
            return self.numerator<=int(other)*self.denominator
        if isinstance(other,numbers.Rational):
            return self.numerator*other.denominator<=other.numerator*self.denominator
        return float(self)<=other
    def __ge__(self,other):
        if isinstance(other,numbers.Integral):
            return self.numerator>=int(other)*self.denominator
        if isinstance(other,numbers.Rational):
            return self.numerator*other.denominator>=other.numerator*self.denominator
        return float(self)>=other
    def __round__(self):
        if any(v<0 for v in self._d.values()):
            return FactoredInt(int(self))
        return FactoredInt(self)
    #def __round__(self,digits):
    def __ceil__(self):
        out=round(self)
        if out>=self:
            return out
        return out+1
    def __floor__(self):
        out=round(self)
        if out<=self:
            return out
        return out-1
    #def __trunc__(self):
    def __contains__(self,x):
        return x in self._d
    def __len__(self):
        return sum(self._d.values())
    def __bool__(self):
        return 0 not in self._d
    def __neg__(self):
        out=FactoredInt({k:min(self._d[k],t._d[k]) for k in self._d.keys() if k!=-1})
        if -1 not in self._d or self._d[-1]%2==0:
            out._d[-1]=1
        return out
    def __abs__(self):
        return FactoredInt({k:min(self._d[k],t._d[k]) for k in self._d.keys() if k!=-1})
    def __copy__(self):
        return FactoredInt({k:min(self._d[k],t._d[k]) for k in self._d.keys()})
    def __hash__(self):
        return hash(self.fraction())
    def __repr__(self):
        return ''.join('FactoredInt({',','.join([':'.join(k,v) for k,v in self._d.items()]),'})')
    def __str__(self):
        if any(v<0 for v in self.values()):
            return ''.join(str(self.numerator),'/',str(self.denominator))
        return str(int(self))
    def __add__(self,other):
        try:
            out=self.gcd(other)
            a=self/out
            b=other/out
            out*=int(a)+int(b)
        except:
            out=self.fraction()+other
        return out
    def __sub__(self,other):
        try:
            out=self.gcd(other)
            a=self/out
            b=other/out
            out*=int(a)-int(b)
        except:
            out=self.fraction()-other
        return out
    def __mul__(self,other):
        try: #Using try/catch for speed, assuming 90% of multiplicands are both FactoredFractions
            return FactoredFraction({x:(self[i]+other[i]) for x in self._d.keys()|other._d.keys()})
        except:
            if isinstance(other, numbers.Rational):
                t=FactoredFraction(other)
                return FactoredFraction({x:(self[i]+t[i]) for x in self._d.keys()|t._d.keys()})
            return self.fraction()*other
    def __truediv__(self,other):
        try:
            return FactoredFraction({x:(self[i]-other[i]) for x in self._d.keys()|other._d.keys()})
        except:
            if isinstance(other, numbers.Rational):
                t=FactoredFraction(other)
                return FactoredFraction({x:(self[i]-t[i]) for x in self._d.keys()|t._d.keys()})
            return self.fraction()/other
    def __floordiv__(self,other):
        try:
            return math.floor(FactoredFraction({x:(self[i]-other[i]) for x in self._d.keys()|other._d.keys()}))
        except:
            if isinstance(other, numbers.Rational):
                t=FactoredFraction(other)
                return math.floor(FactoredFraction({x:(self[i]-other[i]) for x in self._d.keys()|other._d.keys()}))
            return self.fraction()//other
    #def __mod__(self,other):
    #def __divmod__(self,other):
    def __pow__(self,other):
        if isinstance(other,numbers.Integral):
            i=int(other)
            return FactoredFraction({x:(self[i]*i) for x in self._d.keys()})
        return float(self)**other
    #def __radd__(self,other):
    #def __rsub__(self,other):
    #def __rmul__(self,other):
    #def __rtruediv__(self,other):
    #def __rfloordiv__(self,other):
    #def __rmod__(self,other):
    #def __rdivmod__(self,other):
    #def __rpow__(self,other):
    #def __iadd__(self,other):
    #def __isub__(self,other):
    def __imul__(self,other):
        try: #Using try/catch for speed, assuming 90% of multiplicands are both FactoredFractions
            for k,v in other._d.items():
                self[k]=self[k]+v
            return self
        except:
            if isinstance(other, numbers.Rational):
                t=FactoredFraction(other)
                for k,v in t._d.items():
                    self[k]=self[k]+v
                return self
            return NotImplemented
    def __itruediv__(self,other):
        try: #Using try/catch for speed, assuming 90% of multiplicands are both FactoredFractions
            for k,v in other._d.items():
                self[k]=self[k]-v
            return self
        except:
            if isinstance(other, numbers.Rational):
                t=FactoredFraction(other)
                for k,v in t._d.items():
                    self[k]=self[k]-v
                return self
            return NotImplemented
    #def __ifloordiv__(self,other):
    #def __imod__(self,other):
    def __ipow__(self,other):
        if isinstance(other,numbers.Integral):
            i=int(other)
            for x in self._d.keys():
                self[x]*=i
            return self
        return NotImplemented
class Integer(Fraction, numbers.Integral):
    def __setitem__(self,key,value):
        if not isinstance(key,numbers.Integral) or not isinstance(value,numbers.Integral):
            raise TypeError()
        if value<0:
            raise ValueError()
        if value==0:
            del self[key]
        elif key==-1:
            if value%2==0:
                del self[-1]
            else:
                self[-1]=1
        elif key<0:
            self._d[-1]+=value
            self._d[abs(key)]=value
        else:
            self._d[key]=value

if __name__ == '__main__':
    print(int(Fraction(2)*Fraction(2)))