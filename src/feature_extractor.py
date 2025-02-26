import os
import os.path
import numpy as np
import math
import csv
from concurrent.futures import ThreadPoolExecutor
import threading

##
#   Works on python 3.9.13 
#   Fails on python 3.13.0
##

def shortest_path(adj, dimension):
    INF = float('inf')

    dist = np.zeros((dimension, dimension), dtype = float)
    dist[dist == 0] = INF

    temp = np.copy(adj)
    n = 1
    k = 0
    while(n<=dimension):
        if k >= dimension**2:               # We know that the distance matrix got at most dimension squared values to modify
            break                           # Once all values are updated break, since no more updates will happen.

        temp[temp > 0] = 1
        temp = np.matmul(temp,adj)
        n += 1
        for x in range(dimension):
            for y in range(dimension):
                if temp[x][y] > 0:
                    if dist[x][y] == INF:   # Only updates if dist isnt updated yet
                        dist[x][y] = n
                        k += 1              # Counts updates
        
    np.fill_diagonal(dist, 0)
    return dist   

def build_matrices(edges, dimension):
    # generate the adjacency matrix
    adjacency = np.zeros((dimension, dimension), dtype = float)        
    # generate the laplacian matrix
    laplacian = np.zeros((dimension,dimension), dtype = float)
    for edge in edges:
        n1, n2 = edge
        adjacency[n1][n2] = adjacency[n2][n1] = 1

        laplacian[n1][n1] = laplacian[n1][n1] + 1
        laplacian[n2][n2] = laplacian[n2][n2] + 1
        if n1 != n2:
            laplacian[n1][n2] = laplacian[n2][n1] = -1
    return adjacency, laplacian

def process_file(file, path):
    file_path = os.path.join(path, file) # gets the full path to a file
    feature_dict = {}    

    if os.path.isfile(file_path):
        print(file_path)
        f = open( file_path, "r")
        edges = []
        dimension = 0 # value for generating the matrixes later
        feature_dict[file] = {}
        
        #saves the filename to the dictionary
        feature_dict[file]['source'] = file

        # collect data from the file
        for line in f:
            if "c " in line:    # no information here that we need.
                pass
            elif "p edge " in line or "p col " in line or "p edges " in line: # needs to catch 3 different version due to inconsistencies in the files.
                #save the first number as num_vertice and the second as num_edges
                x = line.split()
                dimension = int(x[2])
                feature_dict[file]['num_vertices'] = dimension
                feature_dict[file]['num_edges'] = int(x[3])
            elif "e " in line:
                #add edge to list
                #print(line)
                x = line.split() # splits the line by whitespaces
                n1 = int(x[1]) 
                n2 = int(x[2])
                edges.append((n1-1,n2-1))   # -1 to match 0 indexing.
        f.close()
            
        adjacency, laplacian = build_matrices(edges, dimension) # calls aux method to generate the matrices.
            
        # Find the greatest lenght of all the shortest paths between nodes.
        x = shortest_path(adjacency, dimension) # aux method for making the distance matrix.
        if x.size == 0 or np.all(np.isinf(x)):
            feature_dict[file]['largest_dist'] = np.nan
        else:
            x[x == float('inf')] = 0     
            feature_dict[file]['largest_dist'] = float(np.max(x))

        # do the needed calculations for the matrixes            
        #print(dimension)
        feature_dict[file]['ratio_of_edges'] = float((2*len(edges))/(dimension*(dimension-1)))
        y = np.where(x == np.inf, np.nan, x)    #removes any leftover inf
        feature_dict[file]['average_dist'] = float(np.nanmean(y))  #calculates mean where infs are ignored, helps in cases where a graph is not fully connected
            
        mean = np.mean(np.diag(laplacian))
        feature_dict[file]['mean_degree'] = mean
        #print(feature_dict[file]['mean_degree'])
        variance = np.var(np.diag(laplacian))
        feature_dict[file]['std_deviation_degree'] = math.sqrt(variance)

        # Cubes the adjacency matrix, and then performs trace, which gets the sum of the diagonal elements.
        # then we divide by the number of times a closed triangle is counted
        closed_triplets = np.trace(np.linalg.matrix_power(adjacency, 3)) / 6 # each triangle is counted 6 times (2 permutations per node.)
        #print(closed_triplets)
        if dimension < 3:
            feature_dict[file]['clustering_coef'] = 0
        else:
            total_triplets = dimension * (dimension - 1) * (dimension - 2) / 6  #choose notation.
            ratio = closed_triplets / total_triplets

            feature_dict[file]['clustering_coef'] = ratio
            
        eigenvalue, _ = np.linalg.eig(adjacency)
        abs_eigenvalue = np.absolute(eigenvalue)
        sum = 0.0
        for i in abs_eigenvalue:
            sum = sum + i
        mean = sum/len(abs_eigenvalue)
        feature_dict[file]['energy'] = mean

        sum = 0.0
        for i in eigenvalue:
            sum = sum + i
        mean = sum/len(eigenvalue)

        sum = 0.0
        for i in eigenvalue:
            sum = sum + (i - mean)** 2
        variance = sum/len(eigenvalue)
        feature_dict[file]['std_devi_eig_adj'] = math.sqrt(variance)
            
        eig_list_adj = eigenvalue

        eigenvalue, _ = np.linalg.eig(laplacian)
        eig_list_lap = eigenvalue
        feature_dict[file]['connectivity'] = sorted(eig_list_lap)[1].real
            
        called = False
        small_lap = 0
        sorted_list = sorted(eig_list_lap)
        for i in sorted_list:
            if i != 0:
                called = True
                small_lap = i
                feature_dict[file]['small_nonzero_eig_lap'] = i.real
                break
        if called == False:
            feature_dict[file]['small_nonzero_eig_lap'] = np.nan
            
        called = False
        t = 0       #counter to ensure we don't take the first one.
        for i in sorted_list:
            if i != 0:
                if t == 0:
                    t = 1
                else:
                    called = True
                    feature_dict[file]['sec_small_nonzero_eig_lap'] = i.real
                    break
        if called == False:
            feature_dict[file]['sec_small_nonzero_eig_lap'] = np.nan
            
            
        feature_dict[file]['large_eig_lap'] = sorted_list[-1].real
        large_lap = sorted_list[-1]            
        feature_dict[file]['sec_large_eig_lap'] = sorted_list[-2].real

        sorted_list = sorted(eig_list_adj)

        feature_dict[file]['small_eig_adj'] = sorted_list[0].real
        feature_dict[file]['sec_small_eig_adj'] = sorted_list[1].real
        feature_dict[file]['large_eig_adj'] = sorted_list[-1].real
        feature_dict[file]['sec_large_eig_adj'] = sorted_list[-2].real

        # save largest and second largest eig from adjacency and calc the difference in abs
        gap_adj = abs(sorted_list[-1] - sorted_list[-2]).real
        feature_dict[file]['gap_eig_adj'] = gap_adj
            
        # save the largest and smallest non-zero eig from laplacian and calc the abs difference.        
        gap_lap = abs(large_lap - small_lap).real
        feature_dict[file]['gap_eig_lap'] = gap_lap

        print(f"All features of {file} calculated")# once all files are handled end loop.
    return feature_dict 

def calc_features(path):
    print("Calculating features")
    feature_dict = {}

    col_files = [f for f in os.listdir(path) if f.endswith('.col')] # list generator.
    lock = threading.Lock()

    # Safe thread update function
    def thread_safe_update(features):
        with lock:
            for instance, values in features.items():
                # If the instance already exists in the feature_dict, merge the data
                if instance in feature_dict:
                    # Merge the dictionaries by updating the existing data
                    feature_dict[instance].update(values)
                else:
                    # If the instance does not exist, add it as a new entry
                    feature_dict[instance] = values

    with ThreadPoolExecutor(max_workers=2) as executor:  # Set max_workers based on your CPU
        futures = {executor.submit(process_file, file, path): file for file in col_files}  # Submit all tasks
        for future in futures:
            features = future.result()  # Get the result of the processing
            thread_safe_update(features)  # Update dictionary safely

    return feature_dict 

##
# Takes a path to a directory containing instances, then extracts features from those instances and saves them in a CSV file named InstanceFeatures.csv
##
def generate_feature_file(path):
    # get the features and algorithms used to create a header for the CSV file.
    feature_dict = calc_features(path)
    first_instance_features = list(next(iter(feature_dict.values())).keys()) # gets the headers dynamically.
    header = ['feature_' + feature for feature in first_instance_features]

    filename = "../Resources/InstancesFeatures.csv"
    if os.path.exists(filename):
        existing_instances = set()
        with open(filename, mode = "r", newline="") as file:
            reader = csv.reader(file)
            next(reader,None) # This skips the header file.
            for row in reader:
                if row:
                    existing_instances.add(row[0])
        
        with open(filename, mode = "a", newline="") as file:
            writer = csv.writer(file)
            for feature_source, features in feature_dict.items():
                if feature_source not in existing_instances:
                    row = list(features.values())
                    writer.writerow(row)
        print(f"Updated {filename} with new instances.")
    else:    
        with open(f"../Resources/InstanceFeatures.csv", mode="w", newline="") as file:
            writer = csv.writer(file)

            # write the headers on the first row, followed by the information from the lists on the following rows.
            writer.writerow(header)
            for instance_name, features in feature_dict.items():
                row = list(features.values()) #dynamic addition of the features.

                writer.writerow(row)
                    
        print(f"file: InstanceFeatures.csv created")

def run():
    path = '../Resources/instances'
    generate_feature_file(path)

#static run, is fine as it should always be grabbing from this specified directory.
run()