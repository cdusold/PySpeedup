class Polynomial():
    "This class utilizes dict of keys sparse polynomial implementation."
    #Initialization
    def __init__(self,*args):
        self._d={}
        if len(args)>0:
            if type(args[0]) is dict:
                self._d=args[0]
            else:
                for i,v in enumerate(args):
                    if v!=0:
                        self._d[i]=v

    #Raw value modification methods
    def __copy__(self):
        newone = dict()
        assert newone is not self._d
        for i,v in self.items():
            newone[i]=v
        assert newone is not self._d
        return Polynomial(newone)
    def keys(self):
        return self._d.keys()
    def items(self):
        return self._d.items()
    def __getitem__(self,i):
        if i in self._d:
            return self._d[i]
        else:
            return 0
    def __setitem__(self,i,v):
        if v==0:
            del self[i]
        else:
            self._d[i]=v
    def __delitem__(self,i):
        return self._d.pop(i,None)
    def __contains__(self,i):
        return i in self._d

    #Arithmetic methods
    def __add__(self,other):
        temp=self.__copy__()
        temp+=other
        return temp
    def __radd__(self,other):
        return self+other
    def __iadd__(self,other):
        try:
            for i in set(self.keys()).union(set(other.keys())):
                self[i]=self[i]+other[i]
        except:
            self[0]+=other
        return self
    def __sub__(self,other):
        temp=self.__copy__()
        temp-=other
        return temp
    def __rsub__(self,other):
        temp = -self
        temp+=other
        return temp
    def __isub__(self,other):
        try:
            for i in set(self.keys()).union(set(other.keys())):
                self[i]=self[i]-other[i]
        except:
            self[0]-=other
        return self
    def __mul__(self,other):
        out={}
        try:
            for i in self.keys():
                for j in other.keys():
                    if max>0 and i+j>max:
                        continue
                    out[i+j]=out.get(i+j,0)+self[i]*other[j]
        except:
            for i in self.keys():
                out[i]=self[i]*other
        return Polynomial(out)
    def __rmul__(self,other):
        return self*other
    def __mod__(self,other):
        temp=self.__copy__()
        if type(other) is Polynomial:
            out={}
            o=len(other)
            while len(temp)>o:
                m=len(temp)
                out[m-o]=temp[m]/other[o]
                for i in set(temp.keys()).union(set(x+m-o for x in other.keys())):
                    temp[i]=temp[i]-other[i+o-m]
            temp=Polynomial(out)
        else:
            temp%=other
        return temp
    def __imod__(self,other):
        if type(other) is Polynomial:
            self=self%other
        else:
            for i in set(self.keys()):
                self[i]%=other
        return self
    def __divmod__(self,other):
        out={}
        temp=self.__copy__()
        o=len(other)
        while len(temp)>o:
            m=len(temp)
            out[m-o]=temp[m]/other[o]
            for i in set(temp.keys()).union(set(x+m-o for x in other.keys())):
                temp[i]=temp[i]-other[i+o-m]
        return Polynomial(out),temp
    def __div__(self,other):
        temp=self.__copy__()
        temp/=other
        return temp
    def __idiv__(self,other):
        if other is Polynomial:
            o=len(other)
            while len(self)>o:
                m=len(self)
                for i in set(self.keys()).union(set(x+m-o for x in other.keys())):
                    self[i]=self[i]-other[i+o-m]
        for i in self.keys():
            self[i]/=other
        return self
    def __neg__(self):
        return Polynomial(dict((i,-v) for i,v in self.items()))

    #Evaluates at a specified point.
    def __call__(self,i):
        return sum([i**x*y for x,y in self.items()])

    #Outputs a string representation.
    def __str__(self):
        return '+'.join([''+str(x)+('x' if y==1 else '' if y==0 else 'x^'+str(y)) for y,x in self.items()])
    
    #Outputs a code-based representation.
    def __repr__(self):
        return 'Polynomial('+str(self._d)+')'
    
    #Returns the order of the polynomial assuming positive integer powers. (Instead of length...)
    def __len__(self):
        return max(self.keys())
        