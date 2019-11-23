import time
import pddl
import graph
import expressions
import pathfinding
import sys
import copy
import re

from random import randrange

groundedActions = []
relaxedActions = []


# substitute the var for the value in a list of strings.
def substituteVar(objList, var, value):
    newobj = []
    for o in objList:
        if isinstance(o, list):
            newo = []
            for w in o:
                if not isinstance(w, list):
                    if w == var:
                        w = w.replace(var, value)
                    newo.append(w)
                else:
                    newo.append(substituteVar(w, var, value))
            o = newo
        else:
            if o == var:
                o = o.replace(o, value)
        newobj.append(o)
    return newobj


# make grounded actions recursivelly
def groundRec(ppact, act, param):
    newAct = copy.deepcopy(act)
    if param:
        pp = copy.deepcopy(param)
        np = pp.pop(0)
        for d in np.items():
            newAct2 = copy.deepcopy(newAct)
            for val in d[1]:
                newAct2.precondition = substituteVar(newAct.precondition[:], d[0], val)
                newAct2.effect = substituteVar(newAct.effect[:], d[0], val)
                newAct2.name = newAct.name + " " + d[0] + " - " + val
                groundRec(ppact, newAct2, pp)
    else:
        ppact.append(newAct)
        return ppact
    return ppact


def groundActions(actions, objs):
    for act in actions:
        newparams = []
        for param in act.parameters.items():
            paramList = {}
            paramobjs = objs[param[1]]
            paramList[param[0]] = paramobjs
            newparams.append(paramList)
            paramList = {}
        ppact = []
        groundedActions.extend(groundRec(ppact, act, newparams))
    return groundedActions


def mergeObjsRec(key, vals, items, objs):
    allobjs = []
    # items.pop(key, None)
    for val in vals:
        if val in objs:
            allobjs.extend(objs[val])
        else:
            allobjs.extend(mergeObjsRec(val, items[val], items, objs))
    return allobjs


def mergeObjs(domain, problem):
    # get a list of problem objecst + domain constants
    allobjs = dict(domain.constants)
    for k, v in problem.objects.items():
        allobjs[k] = allobjs[k] + v if k in allobjs else v

    # add the values for the hierarchy types
    types = copy.deepcopy(domain.types)
    alltyps = {}

    for k, v in types.items():
        items = copy.deepcopy(domain.types)
        items.pop(k, None)
        alltyps[k] = []
        alltyps[k] = mergeObjsRec(k, v, items, allobjs)

    # get a list of objects + hierarchy objs
    for k, v in alltyps.items():
        allobjs[k] = allobjs[k] + v if k in allobjs else v

    return allobjs

class PlanNode(graph.Node):
    neighbours = []

    def __init__(self, name, state, objs):
        self.name = name
        self.state = state
        self.objs = objs

    def get_neighbors(self):
        # for each grounded action
        for ac in groundedActions:
            # if the action is modeled in the state
            if expressions.models(self.state, expressions.make_expression(ac.precondition)):
                ## apply the effect to the world
                newstate = expressions.apply(self.state, expressions.make_expression(ac.effect))
                ## add state to the neighbours list as an edge
                nt = PlanNode(ac.name, newstate, self.objs)
                ne = graph.Edge(nt, 1, ac.name)
                self.neighbours.append(ne)
        return self.neighbours

    def get_id(self):
        return str(sorted(self.state.formulas, key=lambda x: str(x.getValue())))

class HeuristicNode(graph.Node):
    neighbours = []

    def __init__(self, name, state, objs):
        self.name = name
        self.state = state
        self.objs = objs

    def get_neighbors(self):
        # for each grounded action
        for ac in groundedActions:
            # if the action is modeled in the state
            if expressions.models(self.state, expressions.make_expression(ac.precondition)):
                ## apply the effect to the world
                newstate = expressions.apply(self.state, expressions.make_expression(ac.effect, True))
                ## add state to the neighbours list as an edge
                nt = HeuristicNode(ac.name, newstate, self.objs)
                ne = graph.Edge(nt, 1, ac.name)
                self.neighbours.append(ne)
        return self.neighbours

    def get_id(self):
        return str(sorted(self.state.formulas, key=lambda x: str(x.getValue())))


def get_goal_atoms(goal):
    goals = []

    if goal[0] in ["and", "or", "not", "=", "imply", "when", "exists", "forall"]:
        goals.extend(get_goal_atoms(goal[1:]))
    else:
        goals.append(goal)
        return goals
    return goals

# # ### & &&& / #& #&&# # ### & #&
def SuperHeuristic(state, action, init, goal, allobjs, isgoal):
    
    # apply action
    supervalue = 0
    actionsApplied = 0
    if isinstance(action, graph.Edge):
        newstate = copy.deepcopy(action.target)
    else:
        newstate = copy.deepcopy(state)
    #goalAtoms = get_goal_atoms(goal)
    

    while not isgoal(newstate):              

        wutnewstate = copy.deepcopy(newstate)
        for rac in groundedActions:
            if expressions.models(newstate.state, expressions.make_expression(rac.precondition)):
                
                bururu = expressions.apply(newstate.state, expressions.make_expression( rac.effect, True))
                for atm in bururu.formulas:
                    if atm not in wutnewstate.state.formulas:
                        wutnewstate.state.formulas.append(atm)

                actionsApplied = actionsApplied + 1
        if actionsApplied == 0:
            return 1000
        actionsApplied = 0
        supervalue = supervalue + 1
        newstate = copy.deepcopy(wutnewstate)

    # return path size    
    return supervalue
    
    #break goal into atoms

    #goalAtoms = get_goal_atoms(goal)
    '''start = HeuristicNode("init", state.state, allobjs)
    (path, cost, visited_cnt, expanded_cnt) = pathfinding.astar(start, pathfinding.default_heuristic, isgoal)
    return len(path)'''
    

def plan(domain, problem, useheuristic=True):
    # get all objects applying the typinh hierarchy
    allobjs = mergeObjs(domain, problem)

    # get all grounded actions
    groundActions(domain.actions, allobjs)
    goalExp = expressions.make_expression(problem.goal)
  
    def isgoal(state):
        return expressions.models(state.state, goalExp)

    def heuristic(state, action):
        return SuperHeuristic(state, action, problem.init, problem.goal, allobjs, isgoal)  # pathfinding.default_heuristic


    start = PlanNode("init", expressions.make_world(problem.init, allobjs), allobjs)
    return pathfinding.astar(start, heuristic if useheuristic else pathfinding.default_heuristic, isgoal)


def main(domain, problem, useheuristic):
    t0 = time.time()
    (path, cost, visited_cnt, expanded_cnt) = plan(pddl.parse_domain(domain), pddl.parse_problem(problem), useheuristic)
    print("visited nodes:", visited_cnt, "expanded nodes:", expanded_cnt)
    if path is not None:
        print("Plan found with cost", cost)
        for n in path:
            print(n.name)
    else:
        print("No plan found")
    print("needed %.2f seconds" % (time.time() - t0))


if __name__ == "__main__":
    # main(sys.argv[1], sys.argv[2], "-d" not in sys.argv)
    main("problems/classical/airport/p06-domain.pddl", "problems/classical/airport/p06-airport2-p2.pddl", True)
    