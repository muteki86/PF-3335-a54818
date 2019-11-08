import planner
import os

path = './problems/classical/elevators-00-strips'

if __name__ == "__main__":
    #main(sys.argv[1], sys.argv[2], "-d" not in sys.argv)
    #planner.main("domain.pddl", "wumpusproblem.pddl", False)
    #main("elevators_domain.pddl", "elevators_s0.pddl", False)
    domain = []
    problems = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if 'domain.pddl' in file:
                domain.append(os.path.join(r, file))
            #if '*.pddl' in file and ('domain.pddl' not in file):
            if '.pddl' in file and ('domain.pddl' not in file):
                problems.append(os.path.join(r, file))
    
    for d in sorted(domain):
        for p in sorted(problems):
            print("Problem: "+p)
            planner.main(d, p, False)
    '''
    print(" DOMAIN ")
    for f in domain:
        print(f)

    print(" PROBLEMS ")
    for f in problems:
        print(f)
    '''
