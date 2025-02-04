import os
 
def read_solution_file(filename):
    with open(filename, 'r') as file:
        return len(set(map(int, [line.split()[0] for line in file])))
 

def load_best_solutions():
    best_solutions = {}
    if not os.path.exists("best_solutions.md"):
        return best_solutions
    
    with open("best_solutions.md", "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("|") and not line.startswith("| Instance") and not line.startswith("|-"):
                parts = line.split("|")
                if len(parts) > 2:
                    instance =  parts[1].strip()
                    best_bound = int(parts[2].strip())
                    best_solutions[instance] = best_bound

    return best_solutions

def update_best_solutions():
    best_solutions = load_best_solutions()

    for solution_file in os.listdir("solutions"):
        instance = solution_file.replace(".sol", ".col")
        new_bound = read_solution_file(os.path.join("solutions", solution_file))
        if new_bound < best_solutions.get(instance, float("inf")):
            best_solutions[instance] = new_bound
 
    with open("best_solutions.md", "w") as file:
        file.write("# Best Solutions for Graph Coloring Instances\n\n")
        file.write("| Instance | Best Upper Bound |\n")
        file.write("|----------|------------------|\n")
        for instance, bound in best_solutions.items():
            file.write(f"| {instance} | {bound} |\n")
 
if __name__ == "__main__":
    update_best_solutions()
