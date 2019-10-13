import graph
import time
from datetime import timedelta


def default_heuristic(n, edge):
    """
    Default heuristic for A*. Do not change, rename or remove!
    """
    return 0

def contains(frontier, node):
    for n in frontier:
        if n[0].get_id() == node.get_id():
            return True
    return False


def updateValue(frontier, newValue):
    for n in frontier:
        if n[0].get_id() == newValue[0].get_id() and (n[1] + n[2]) > (newValue[1] + newValue[2]):
            frontier.remove(n)
            frontier.append(newValue)
            return
    return 

def astar(start, heuristic, goal):
    
    expanded = []
    visited = []
    path = []
    frontier = []
    
    #path.append(start)
    frontier.append((start, 0,heuristic(start, goal), path))
    visited.append(start.get_id())

    while len(frontier) > 0:
        current, cdist, h, path = frontier.pop(0)
        if(goal(current)):
            return path,cdist,len(visited),len(expanded)

        expanded.append(current.get_id())
        for edge in current.get_neighbors():
            if edge.target.get_id() not in expanded:
                cost = cdist+edge.cost
                h = heuristic(edge.target,edge)
                if contains(frontier, edge.target):
                    updateValue(frontier,(edge.target,cost,h,path+[edge]))
                else:
                    frontier.append((edge.target,cost,h,path+[edge]))
                    visited.append(edge.target.get_id())
                frontier.sort(key = lambda n: n[1] + n[2])

    #raise RuntimeError("A* failed to find a solution")

    return None,None,len(visited),len(expanded)
    return [], 0, 0,0

def print_path(result):
    (path,cost,visited_cnt,expanded_cnt) = result
    print("visited nodes:", visited_cnt, "expanded nodes:",expanded_cnt)
    if path:
        print("Path found with cost", cost)
        for n in path:
            print(n.name)
    else:
        print("No path found")
    print("\n")

def main():
    """
    You are free (and encouraged) to change this function to add more test cases.
    
    You are provided with three test cases:
        - pathfinding in Austria, using the map shown in class. This is a relatively small graph, but it comes with an admissible heuristic. Below astar is called using that heuristic, 
          as well as with the default heuristic (which always returns 0). If you implement A* correctly, you should see a small difference in the number of visited/expanded nodes between the two heuristics.
        - pathfinding on an infinite graph, where each node corresponds to a natural number, which is connected to its predecessor, successor and twice its value, as well as half its value, if the number is even.
          e.g. 16 is connected to 15, 17, 32, and 8. The problem given is to find a path from 1 to 2050, for example by doubling the number until 2048 is reached and then adding 1 twice. There is also a heuristic 
          provided for this problem, but it is not admissible (think about why), but it should result in a path being found almost instantaneously. On the other hand, if the default heuristic is used, the search process 
          will take a noticeable amount (a couple of seconds).
        - pathfinding on the same infinite graph, but with infinitely many goal nodes. Each node corresponding to a number greater 1000 that is congruent to 63 mod 123 is a valid goal node. As before, a non-admissible
          heuristic is provided, which greatly accelerates the search process. 
    """
    start_time = time.time()	# LINE ADDED for track excution time for performance benchmarking
    target = "Bregenz"
    def atheuristic(n, edge):
        return graph.AustriaHeuristic[target][n.get_id()]
    def atgoal(n):
        return n.get_id() == target
    
    result = astar(graph.Austria["Eisenstadt"], atheuristic, atgoal)
    print_path(result)
    
    result = astar(graph.Austria["Eisenstadt"], default_heuristic, atgoal)
    print_path(result)
    
    target = 2050
    def infheuristic(n, edge):
        return abs(n.get_id() - target)
    def infgoal(n):
        return n.get_id() == target
    
    result = astar(graph.InfNode(1), infheuristic, infgoal)
    print_path(result)
    
    result = astar(graph.InfNode(1), default_heuristic, infgoal)
    print_path(result)
    
    def multiheuristic(n, edge):
        return abs(n.get_id()%123 - 63)
    def multigoal(n):
        return n.get_id() > 1000 and n.get_id()%123 == 63
    
    result = astar(graph.InfNode(1), multiheuristic, multigoal)
    print_path(result)
    
    result = astar(graph.InfNode(1), default_heuristic, multigoal)
    print_path(result)
    print("Elapsed time: %s" % (str(timedelta(seconds= time.time() - start_time)))) # LINE ADDED to report elapsed time for performance benchmarking
    

if __name__ == "__main__":
    main()
