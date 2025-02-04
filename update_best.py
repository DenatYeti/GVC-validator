import os
 
BEST_SOLUTIONS_FILE = "best_solutions.md"
SOLUTIONS_DIR = "solutions"

def read_solution_file(filename):
    with open(filename, 'r') as file:
        colors = set()
        for line in file:
            line = line.strip()
            if line:  # Ignore empty lines
                colors.add(int(line.split()[0]))  # Extract first number (color)
        return len(colors)


def load_best_solutions():
    """ Reads best_solutions.md and returns a dictionary of best known bounds. """
    best_solutions = {}

    if not os.path.exists(BEST_SOLUTIONS_FILE):
        return best_solutions  # Return empty if file does not exist

    with open(BEST_SOLUTIONS_FILE, "r") as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split("|")
            if len(parts) == 3 and parts[0] == "":  # Ensure correct table format
                instance = parts[1].strip()
                try:
                    best_bound = int(parts[2].strip())
                    best_solutions[instance] = best_bound
                except ValueError:
                    print(f"Skipping malformed entry in {BEST_SOLUTIONS_FILE}: {line.strip()}")
    
    return best_solutions

def update_best_solutions():
    """ Updates the best_solutions.md file with new best bounds. """
    best_solutions = load_best_solutions()

    # Ensure solutions directory exists
    if not os.path.exists(SOLUTIONS_DIR):
        print(f"Solutions directory '{SOLUTIONS_DIR}' not found.")
        return

    found_new_best = False
    for solution_file in os.listdir(SOLUTIONS_DIR):
        if solution_file.endswith(".sol"):
            instance = solution_file.replace(".sol", ".col")
            new_bound = read_solution_file(os.path.join(SOLUTIONS_DIR, solution_file))
            
            if new_bound < best_solutions.get(instance, float("inf")):
                print(f"New best solution for {instance}: {new_bound} (previous: {best_solutions.get(instance, 'N/A')})")
                best_solutions[instance] = new_bound
                found_new_best = True

    # If no updates, exit early
    if not found_new_best:
        print("No new best solutions found. Markdown file remains unchanged.")
        return

    # Write updated best solutions
    with open(BEST_SOLUTIONS_FILE, "w") as file:
        file.write("# Best Solutions for Graph Coloring Instances\n\n")
        file.write("| Instance | Best Upper Bound |\n")
        file.write("|----------|------------------|\n")
        for instance, bound in sorted(best_solutions.items()):
            file.write(f"| {instance} | {bound} |\n")


 
if __name__ == "__main__":
    update_best_solutions()
