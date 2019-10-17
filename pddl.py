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

def parse_domain(fname):
    
    domain_name = ''
    requirements = []
    types = []
    actions = []
    predicates = []
    constants = []

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
                types = tkn
            elif hdr == ':constants':
                acon = tkn 
                while acon:
                    acn = acon.pop(0)
                    acd = acon.pop(0)
                    act = acon.pop(0)
                    constants.append((acn, act))
            elif hdr == ':predicates':
                while tkn:
                    apred = tkn.pop(0) # read predicate
                    while apred:
                        predname = apred.pop(0) # read name
                        predparams = []
                        predvarnames = []
                        while apred:
                            # read names until - 
                            r = apred.pop(0)
                            if r != "-":
                                predvarnames.append(r)
                            else: 
                                # when - , read next as type
                                typ = apred.pop(0)
                                # insert each name with the type
                                for pn in predvarnames:
                                    predparams.append((pn, typ))
                                predvarnames = []
                        # if fin and still names in the queue, insert them as type ''
                        for pn in predvarnames:
                            predparams.append((pn, ''))

                        predicates.append(Predicate(predname, predparams))
            elif hdr == ':action':
                aname = tkn.pop(0)
                aparameters = []
                aprecondition = ''           
                aeffect = ''
                while tkn:
                    atkn = tkn.pop(0)
                    if atkn == ':parameters':
                        aparam = tkn.pop(0) # get the parameters
                        while aparam: # while we have info in the parameters
                            p = aparam.pop(0) # parameter name
                            if len(aparam) > 0:
                                d = aparam.pop(0)
                                if d == "-":
                                    typ = aparam.pop(0) # type
                                    aparameters.append((p,typ)) # add (parameter, type)
                                else:
                                    aparameters.append((p,''))
                            else:
                                aparameters.append((p,''))
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
    goal = []

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
                 # read predicate
                objvarnames = []
                while tkn:
                    objname = tkn.pop(0) # read name
                    if objname != "-":
                        objvarnames.append(objname)
                    else: 
                        # when - , read next as type
                        typ = tkn.pop(0)
                        # insert each name with the type
                        for pn in objvarnames:
                            objects.append((pn, typ))
                        objvarnames = []
                # if fin and still names in the queue, insert them as type ''
                for pn in objname:
                    objects.append((pn, ''))
            elif hdr == ':init':
                init = tkn
            elif hdr == ':goal':
                goal = tkn

    return Problem(problem, domain_name, objects, init, goal)
    
if __name__ == "__main__":
    print(parse_domain("domain.pddl"))
    print(parse_problem("wumpusproblem.pddl"))

    #print(parse_domain(sys.argv[1]))
    #print(parse_problem(sys.argv[2]))

