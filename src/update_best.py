import os
 
def read_solution_file(filename):
    with open(filename, 'r') as file:
        return len(set(map(int, [line.split()[0] for line in file])))
 

def load_best_solutions():
    best_solutions = {}
    if not os.path.exists("../docs/best/best_solutions.md"):
        return best_solutions
    
    with open("../docs/best/best_solutions.md", "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("|") and not line.startswith("| Instance") and not line.startswith("|-"):
                parts = line.split("|")
                if len(parts) > 2:
                    instance =  parts[1].strip()
                    best_bound = int(parts[2].strip())
                    best_solutions[instance]= best_bound

    return best_solutions

def update_best_solutions():
    best_solutions = load_best_solutions()
    algos = {}

    for root, _, files in os.walk("../Resources/solutions"):
        algorithm = os.path.basename(root)
        for file in files:
            if file.endswith(".sol"):
                solution_file = os.path.join(root, file)
                instance_name, _ = os.path.splitext(file)
                instance = instance_name + ".col"

                new_bound = read_solution_file(solution_file)
                if new_bound < best_solutions.get(instance, float("inf")):
                    best_solutions[instance] = new_bound
                    algos[instance] = algorithm
    
    with open("../docs/best/best_solutions.md", "w") as file:
        file.write("# Best Solutions for Graph Coloring Instances\n\n")
        file.write("| Instance | Best Upper Bound | Algorithm\n")
        file.write("|----------|------------------|-----------|\n")
        for instance, bound in best_solutions.items():
            algo = algos.get(instance, "Unknown")
            file.write(f"| {instance} | {bound} | {algo} |\n")
 
if __name__ == "__main__":
    update_best_solutions()
