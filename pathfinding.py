import graph
import time
from datetime import timedelta


def default_heuristic(n, edge):
    """
    Default heuristic for A*. Do not change, rename or remove!
    """
    return 0


def astar(start, heuristic, goal):
    """
    A* search algorithm. The function is passed a start graph.Node object, a heuristic function, and a goal predicate.

    The start node can produce neighbors as needed, see graph.py for details.

    The heuristic is a function that takes two parameters: a node, and an edge. The algorithm uses this heuristic to determine which node to expand next.
    Note that, unlike in classical A*, the heuristic can also use the edge used to get to a node to determine the node's heuristic value. This can be beneficial when the
    edges represent complex actions (as in the planning case), and we want to take into account the differences produced by that action.

    The goal is also represented a function, that is passed a node, and returns True if that node is a goal node, otherwise False. This representation was also chosen to
    simplify implementing the planner later, which can use the functions developed in task 1 to determine if a state models the goal condition,
    but is otherwise equivalent to classical A*.

    The function should return a 4-tuple (path,distance,visited,expanded):
        - path is a sequence of graph.Edge objects that have to be traversed to reach a goal state from the start.
        - distance is the sum of costs of all edges in the path
        - visited is the total number of nodes that were added to the frontier during the execution of the algorithm
        - expanded is the total number of nodes that were expanded (i.e. whose neighbors were added to the frontier)
    """
    G = {}  # Actual movement cost to each position from the start position
    F = {}  # Estimated movement cost of start to end going via this position

    path = []
    distance = 0
    visited = 0
    expanded = 0

    # Initialize starting values
    G[start.get_id()] = 0
    F[start.get_id()] = heuristic(start, goal)

    closedVertices = []
    openVertices = [start]
    cameFrom = {}

    while len(openVertices) > 0:

		# Get the vertex in the open list with the lowest F score
        current = None
        currentFscore = None
        #sort F by value

        for pos in openVertices:
                if current is None or F[pos.get_id()] < currentFscore:
                    currentFscore = F[pos.get_id()]
                    current = pos

        # Check if we have reached the goal
        if goal(current):
            # Retrace our route backward

            path = []
            totalCost = 0
            for vert in cameFrom:
                if vert[1] == current.get_id():
                    currentId = vert
            
            while currentId in cameFrom:
                currentNode = cameFrom[currentId]
                path.append(currentNode)
                totalCost= totalCost + currentNode.cost
                if(currentId[0] == start.get_id() ): 
                    break
                for vert in cameFrom:
                    if vert[1] == currentId[0]:
                        currentId = vert
                        continue
                
            #path.reverse()
            
            return path[::-1], totalCost, visited, expanded
            

        # Mark the current vertex as closed
        openVertices.remove(current)
        expanded = expanded + 1
        closedVertices.append(current)

        # Update scores for vertices near the current position
        for neighbour in current.get_neighbors():
            
            if neighbour.target in closedVertices: 
                continue #We have already processed this node exhaustively
            candidateG = G[current.get_id()] + neighbour.cost

            if neighbour.target not in openVertices:
                openVertices.append(neighbour.target) #Discovered a new vertex
                visited = visited + 1
            elif candidateG >= G[neighbour.target.get_id()]:
                continue #This G score is worse than previously found

            #Adopt this G score
            cameFrom[(current.get_id(),neighbour.target.get_id())] = neighbour
            G[neighbour.target.get_id()] = candidateG
            H = heuristic(neighbour.target, goal)
            F[neighbour.target.get_id()] = G[neighbour.target.get_id()] + H

    raise RuntimeError("A* failed to find a solution")


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
    
    result = astar(graph.InfNode(1), infheuristic, multigoal)
    print_path(result)
    
    result = astar(graph.InfNode(1), default_heuristic, multigoal)
    print_path(result)
    print("Elapsed time: %s" % (str(timedelta(seconds= time.time() - start_time)))) # LINE ADDED to report elapsed time for performance benchmarking
    

if __name__ == "__main__":
    main()
