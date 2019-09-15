from copy import deepcopy

class LogicalFormula:

    def isModeledBy(self, world):
        return False

    def substitute(self, variable, value):
        return self


# "and" with *arbitrarily many parameters*
class And(LogicalFormula):
    children = []
    def __init__(self, param1):
        self.children = param1
        super(LogicalFormula, self).__init__()

    def get_new(self):
        return (self).__class__(self.children)
    
    def isModeledBy(self, world):
        for c in self.children:
            if not c.isModeledBy(world):
                return False
        return True

    def apply(self, world):
        for c in self.children:
            c.apply(world)

    def substitute(self, variable, value):
        for c in self.children:
            c.substitute(variable, value)

class Atom(LogicalFormula):

    def __init__(self, param1):
        self.param1 = param1
        super(LogicalFormula, self).__init__()
    
    def getValue(self):
        return self.param1

    def isModeledBy(self, world):
        for t in world.formulas:
            if self.param1 == t.getValue():
                return True
        return False

    def __repr__(self):
        return str(self.param1)

    def get_new(self):
        return (self).copy()
    
    def apply(self, world, isDelete=False):
        for t in world.formulas:
            if self.param1 == t.getValue():
                if isDelete:
                    world.formulas.remove(t)
                    return
                else: 
                    return
        world.formulas.append(self)
    
    def substitute(self, variable, value):
        lst = list(self.param1)
        lst[lst.index("?l")] = value
        self.param1 = tuple(lst)
        #self.param1[self.param1.index("?l")] = variable
    
a = And([("on", "a", "b"), ("on", "a", "d")])
print(a)
b = a.get_new()
c = b
print(b)
print(a==b)
print(b==c)


    
