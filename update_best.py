import os
 
def read_solution_file(filename):
    with open(filename, 'r') as file:
        return len(set(map(int, [line.split()[1] for line in file])))
 
def update_best_solutions():
    best_solutions = {}
    with open("best_solutions.md", "r") as file:
        for line in file:
            if line.startswith("| instance"):
                instance = line.split("|")[1].strip()
                best_bound = int(line.split("|")[2].strip())
                best_solutions[instance] = best_bound
 
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
