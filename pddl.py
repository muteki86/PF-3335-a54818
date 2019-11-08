import sys
import expressions
import re


class Domain:
    def __init__(self, domain_name, requirements, types, actions, predicates, constants):
        self.domain_name = domain_name
        self.requirements = requirements
        self.types = types
        self.actions = actions
        self.predicates = predicates
        self.constants = constants 

class Action:
    def __init__(self, name, parameters, precondition, effect):
        self.name = name
        self.parameters = parameters
        self.precondition = precondition
        self.effect = effect

class Predicate:
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters

class Problem:
    def __init__(self, problem, domain_name, objects, init, goal):
        self.problem = problem
        self.domain_name = domain_name
        self.objects = objects
        self.init = init
        self.goal = goal


def tokenize(fstr):
    tokens = []
    tknByOP = fstr.split(" ") # split by spaces
    for str1 in tknByOP:    
        if len(str1) >0: # if the line is not empty
            tokens.extend([tkn for tkn in re.split('([()])', str1) if len(tkn) > 0]) # split by parenthesis and add to list all elements that are not empty
    return tokens

def parsefile(filename):
    tokens = []
    allstr = [line.strip() for line in open(filename)]
    
    for line in allstr:
        if not line.startswith(";"):
            tokens.extend(tokenize(line.replace('\t', '').lower()))

    stack = []
    list = []
    #tokenize
    for tkn in tokens:
        if tkn == ")":
            # pop the list until the opening parenthesis is found
            list = []
            ctkn = stack.pop()
            while ctkn != "(":
                list.insert(0,ctkn)
                ctkn = stack.pop()
            stack.append(list)
        else:
            stack.append(tkn)
    return stack.pop(0)

supported_reqs = [':strips', ':disjunctive-preconditions', ':typing', ':equality', ':existential-preconditions', ':universal-preconditions', ':conditional-effects', ':adl']

def parseTypes(tkn, addall=False):
    typeParam = {}
    typevarnames = []
    allobjs = []
    while tkn:
        r = tkn.pop(0)
        if r != "-":
            typevarnames.append(r)
            allobjs.append(r)
        else: 
            typ = tkn.pop(0)
            if typ in typeParam:
                typeParam[typ] = typeParam[typ] + typevarnames
            else:
                typeParam[typ] =  typevarnames
            
            typevarnames = []
    # if fin and still names in the queue, insert them as type ''
    if len(typevarnames) > 0:
        typeParam[""] = typevarnames
    if addall: 
        typeParam[""] = allobjs
    return typeParam

def parseParams(tkn):
    typeParam = {}
    typevarnames = []
    while tkn:
        r = tkn.pop(0)
        if r.startswith("?"):
            typevarnames.append(r)
        else:
            if r == "-":
                typ = tkn.pop(0)
                for pr in typevarnames:
                    typeParam[pr] = typ
                typevarnames = []
    
    if len(typevarnames) > 0:
        for pr in typevarnames:
            typeParam[pr] = ""
    return typeParam

def parse_domain(fname):
    
    domain_name = ''
    requirements = []
    types = {}
    actions = []
    predicates = []
    constants = {}

    tokens = parsefile(fname)
    tkn = tokens.pop(0)

    if tkn == "define":
        while tokens:
            tkn = tokens.pop(0)
            hdr = tkn.pop(0)
            if hdr == 'domain':
                domain_name = tkn[0]
            elif hdr == ':requirements':
                for req in tkn:
                        if not req in supported_reqs:
                            raise Exception('Invalid requirement:' + req)
                requirements = tkn
            elif hdr == ':types':
                types = parseTypes(tkn)
            elif hdr == ':constants':
                constants = parseTypes(tkn, True)
            elif hdr == ':predicates':
                while tkn:
                    apred = tkn.pop(0) # read predicate
                    while apred:
                        predname = apred.pop(0) # read name
                        predParams = []
                        predParams = parseTypes(apred)
                        predicates.append(Predicate(predname, predParams))

            elif hdr == ':action':
                aname = tkn.pop(0)
                aparameters = []
                aprecondition = ''           
                aeffect = ''
                while tkn:
                    atkn = tkn.pop(0)
                    if atkn == ':parameters':
                        aparam = tkn.pop(0) # get the parameters
                        aparameters = parseParams(aparam)
                    elif atkn == ':precondition':
                        aprecondition = tkn.pop(0)
                    elif atkn == ':effect':
                        aeffect = tkn.pop(0)
                actions.append(Action(aname, aparameters, aprecondition, aeffect))
    
    return Domain(domain_name, requirements, types, actions, predicates, constants) 
    
def parse_problem(fname):
    problem = ''
    domain_name = ''
    objects = []
    init = []

    tokens = parsefile(fname)
    tkn = tokens.pop(0)
    if tkn == "define":
        while tokens:
            tkn = tokens.pop(0)
            hdr = tkn.pop(0)
            if hdr == ':domain':
                domain_name = tkn[0]
            elif hdr == 'problem':
                problem = tkn[0]
            elif hdr == ':objects':
                objects = parseTypes(tkn, True)
            elif hdr == ':init':
                init = tkn
            elif hdr == ':goal':
                goal = expressions.make_expression(tkn.pop(0))

    return Problem(problem, domain_name, objects, init, goal)
    
if __name__ == "__main__":
    print(parse_domain(sys.argv[1]))
    print(parse_problem(sys.argv[2]))

