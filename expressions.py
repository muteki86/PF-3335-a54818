
import time
import copy
from datetime import timedelta


class World:
    def __init__(self, formulas, sets):
        self.formulas = formulas
        self.sets = sets

    def get_new(self):
        return (self).__class__(copy.deepcopy(self.formulas), copy.deepcopy(self.sets))

    def __eq__(self, other):
        selfFormulas = str(sorted(self.formulas, key=lambda x: str(x.getValue())))
        otherFormulas = str(sorted(other.formulas, key=lambda x: str(x.getValue())))

        if selfFormulas == otherFormulas:
            return True
        return False

class LogicalFormula:

    isRelaxed = False

    def isModeledBy(self, world):
        return False

    def substitute(self, variable, value):
        return self

# "and" with *arbitrarily many parameters*
class And(LogicalFormula):
    def __init__(self, param1):
        self.children = param1
        super(LogicalFormula, self).__init__()

    def get_new(self):
        newc = []
        for c in self.children:
            newc.append(c.get_new())
        return (self).__class__(newc)
    
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

#- "or" with *arbitrarily many parameters*
class Or(LogicalFormula):
    def __init__(self, param1):
        self.children = param1
        super(LogicalFormula, self).__init__()
    
    def get_new(self):
        newc = []
        for c in self.children:
            newc.append(c.get_new())
        return (self).__class__(newc)

    def isModeledBy(self, world):
        for c in self.children:
            if c.isModeledBy(world):
                return True
        return False
    
    def substitute(self, variable, value):
        for c in self.children:
            c.substitute(variable, value)

#- "not" with exactly one parameter 
class Not(LogicalFormula):
    def __init__(self, param1):
        self.param1 = param1
        super(LogicalFormula, self).__init__()
    
    def get_new(self):
        return (self).__class__(self.param1.get_new())

    def isModeledBy(self, world):
        return not self.param1.isModeledBy(world)
    
    def apply(self, world):
        self.param1.apply(world, True)
    
    def substitute(self, variable, value):
        self.param1.substitute(variable, value)

#- "imply" with exactly two parameters 
class Imply(LogicalFormula):
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
        super(LogicalFormula, self).__init__()

    def isModeledBy(self, world):
        return not self.param1.isModeledBy(world) or self.param2.isModeledBy(world)
    
    def get_new(self):
        return (self).__class__(self.param1.get_new(),self.param2.get_new())
    
    def substitute(self, variable, value):
        self.param1.substitute(variable, value)
        self.param2.substitute(variable, value)

#- "=" with exactly two parameters which are variables or constants
class Equals(LogicalFormula):
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
        super(LogicalFormula, self).__init__()
    
    def isModeledBy(self, world):
        return self.param1 == self.param2

    def get_new(self):
        return (self).__class__(self.param1,self.param2)

    def substitute(self, variable, value):
        if str(self.param1) == str(variable):
            self.param1 = value
        if str(self.param2) == str(variable):
            self.param2 = value

#- "when" with exactly two parameters 
class When(LogicalFormula):
    def __init__(self, precon, effect):
        self.precon = precon
        self.effect = effect
        super(LogicalFormula, self).__init__()
    
    def get_new(self):
        return (self).__class__(self.precon.get_new(),self.effect.get_new())

    def apply(self, world):
        if self.precon.isModeledBy(world):
            self.effect.apply(world)

    def substitute(self, variable, value):
        self.effect.substitute(variable, value)
        self.precon.substitute(variable, value)

#- "exists" with exactly two parameters, where the first one is a variable specification
class Exists(LogicalFormula):
    def __init__(self, domain, variable, param2):
        self.variable = variable
        self.domain = domain
        self.param2 = param2
        super(LogicalFormula, self).__init__()
    
    def isModeledBy(self, world):
        values = world.sets[self.domain]

        for value in values:
            subsParam = substitute(self.param2, self.variable, value)
            if subsParam.isModeledBy(world): 
                return True
        return False

    def get_new(self):
        return (self).__class__(self.domain, self.variable,self.param2.get_new())

#- "forall" with exactly two parameters, where the first one is a variable specification
class Forall(LogicalFormula):
    def __init__(self, domain, variable, param2):
        self.variable = variable
        self.domain = domain
        self.param2 = param2
        super(LogicalFormula, self).__init__()

    def isModeledBy(self, world):
        values = world.sets[self.domain]
        newParams = [] 

        for value in values:
            subsParam = substitute(self.param2, self.variable, value)
            newParams.append(subsParam)

        for np in newParams:
            if not np.isModeledBy(world): 
                return False 
        return True

    def substitute(self, variable, value):
        self.param2.substitute(variable, value)

    def apply(self, world):
        values = world.sets[self.domain]
        newParams = [] 

        for value in values:
            subsParam = substitute(self.param2, self.variable, value)
            newParams.append(subsParam)

        for np in newParams:
            np.apply(world)

    def get_new(self):
        return (self).__class__(self.domain, self.variable,self.param2.get_new())

class Atom(LogicalFormula):
    def __init__(self, param1, isRelaxed=False):
        self.param1 = param1
        self.isRelaxed = isRelaxed
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

    def __eq__(self, other):
        if self.param1 == other.param1:
            return True
        return False

    def get_new(self):
        return (self).__class__(self.param1+tuple())
    
    def apply(self, world, isDelete=False):
        for t in world.formulas:
            if self.param1 == t.getValue():
                if isDelete and not self.isRelaxed:
                    world.formulas.remove(t)
                    return
                else: 
                    return
        world.formulas.append(self)
    
    def substitute(self, variable, value):
        lst = list(self.param1)
        if variable in lst :
            lst[lst.index(variable)] = value
            self.param1 = tuple(lst)


def models(world, condition):
    return condition.isModeledBy(world)

def substitute(expression, variable, value):
    newexp = expression.get_new()
    newexp.substitute(variable, value)
    return newexp

def apply(world, effect):
    braveNewWorld = world.get_new()
    effect.apply(braveNewWorld)
    return braveNewWorld

def make_world(atoms, sets):
    formulas = []
    for exp in atoms:
        atom1 = Atom(tuple(exp))
        formulas.append(atom1)   

    world = World(formulas, sets)
    return world

def make_expression(ast, isRelaxed=False):
    if ast[0] in ["and", "or", "not", "=", "imply", "when", "exists", "forall"]:
        if ast[0] == "and" or ast[0] == "or":
            children = []
            for c in ast[1:]:
                children.append(make_expression(c,isRelaxed))
            return And(children) if ast[0] == "and" else Or(children)
        elif ast[0] == "not":
            return Not(make_expression(ast[1],isRelaxed))
        elif ast[0] == "=":
            return Equals(ast[1], ast[2])
        elif ast[0] == "imply":
            return Imply(make_expression(ast[1],isRelaxed), make_expression(ast[2],isRelaxed))
        elif ast[0] == "when":
            return When(make_expression(ast[1],isRelaxed), make_expression(ast[2],isRelaxed))
        elif ast[0] == "exists":
            return Exists(ast[1][2], ast[1][0], make_expression(ast[2],isRelaxed))
        elif ast[0] == "forall":
            return Forall(ast[1][2],ast[1][0], make_expression(ast[2],isRelaxed))
    else:
        a = Atom(tuple(ast), isRelaxed)
        return a
    return None

if __name__ == "__main__":
    start_time = time.time()	# LINE ADDED for track excution time for performance benchmarking
    exp = make_expression(("or", ("on", "a", "b"), ("on", "a", "d")))
    world = make_world([("on", "a", "b"), ("on", "b", "c"), ("on", "c", "d")], {})
    
    print("Should be True: ", end="")
    print(models(world, exp))
    change = make_expression(["and", ("not", ("on", "a", "b")), ("on", "a", "c")])
    
    print("Should be False: ", end="")
    print(models(apply(world, change), exp))
    
    
    print("mickey/minny example")
    world = make_world([("at", "store", "mickey"), ("at", "airport", "minny")], {"Locations": ["home", "park", "store", "airport", "theater"], "": ["home", "park", "store", "airport", "theater", "mickey", "minny"]})
    exp = make_expression(("and", 
        ("not", ("at", "park", "mickey")), 
        ("or", 
              ("at", "home", "mickey"), 
              ("at", "store", "mickey"), 
              ("at", "theater", "mickey"), 
              ("at", "airport", "mickey")), 
        ("imply", 
                  ("friends", "mickey", "minny"), 
                  ("forall", 
                            ("?l", "-", "Locations"),
                            ("imply",
                                    ("at", "?l", "mickey"),
                                    ("at", "?l", "minny"))))))
                                    
    print("Should be True: ", end="")
    print(models(world, exp))
    become_friends = make_expression(("friends", "mickey", "minny"))
    friendsworld = apply(world, become_friends)
    print("Should be False: ", end="")
    print(models(friendsworld, exp))
    move_minny = make_expression(("and", ("at", "store", "minny"), ("not", ("at", "airport", "minny"))))
    
    movedworld = apply(friendsworld, move_minny)
    print("Should be True: ", end="")
    print(models(movedworld, exp))
    
    
    move_both_cond = make_expression(("and", 
                                           ("at", "home", "mickey"), 
                                           ("not", ("at", "store", "mickey")), 
                                           ("when", 
                                                 ("at", "store", "minny"), 
                                                 ("and", 
                                                      ("at", "home", "minny"), 
                                                      ("not", ("at", "store", "minny"))))))
                                                      
    
    print("Should be True: ", end="")
    print(models(apply(movedworld, move_both_cond), exp))
    
    print("Should be False: ", end="")
    print(models(apply(friendsworld, move_both_cond), exp))
    
    exp1 = make_expression(("forall", 
                            ("?l", "-", "Locations"),
                            ("forall",
                                  ("?l1", "-", "Locations"),
                                  ("imply", 
                                       ("and", ("at", "?l", "mickey"),
                                               ("at", "?l1", "minny")),
                                       ("=", "?l", "?l1")))))
                                       
    print("Should be True: ", end="")
    print(models(apply(movedworld, move_both_cond), exp1))
    
    print("Should be False: ", end="")
    print(models(apply(friendsworld, move_both_cond), exp1))

    print("Elapsed time: %s" % (str(timedelta(seconds= time.time() - start_time)))) # LINE ADDED to report elapsed time for performance benchmarking