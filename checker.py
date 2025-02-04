import sys
 
def read_dimacs_file(filename):
    with open(filename, 'r') as file:
        edges = []
        for line in file:
            if line.startswith('e'):
                _, v1, v2 = line.split()
                edges.append((int(v1), int(v2)))
    return edges
 
def read_solution_file(filename):
    with open(filename, 'r') as file:
        colors = {}
        i = 0
        for line in file:
            vertex = i
            i += 1
            color = line
            colors[vertex] = color
    return colors
 
def check_solution(dimacs_file, solution_file):
    edges = read_dimacs_file(dimacs_file)
    colors = read_solution_file(solution_file)
    for v1, v2 in edges:
        if colors[v1] == colors[v2]:
            return False, f"Invalid coloring: vertices {v1} and {v2} have the same color"
    return True, "Valid coloring"
 
if __name__ == "__main__":
    dimacs_file = sys.argv[1]
    solution_file = sys.argv[2]
    valid, message = check_solution(dimacs_file, solution_file)
    print(message)
    if not valid:
        sys.exit(1)