# This program is meant to take .col files and extract feature data from them.
#   This involves reading data from the file, generating laplacian and adjacency graphs, and performing the necessary calculations.
import os
import os.path
import numpy as np
import csv
import time 
import argparse

def gather_features(path):
    print("Calculating features")
    feature_dict = {}

    with open(path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = row['feature_source']
            row.pop('feature_source')
            feature_dict[key] = row

    return feature_dict 

##
# This should open the best.csv file and treat it as the solutions from an algorithm
#   This method assumes that all solutions passed to it are valid, this is done since i want to use the github action to check the validity of solutions instead.
#       Could consider having the action delete non valid solutions.
##
def algo_performance(algos, feature_dict,path_to_best): 
    print("Processing Algorithm results...")

    algo_dict = {}
    best_dict = {}

    with open(path_to_best, mode='r',newline='',encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = row['Source']
            row.pop('Source')
            best_dict[key] = row
            
    for instance_name in feature_dict:
        algo_dict[instance_name] = {}
        algo_dict[instance_name]['best_performance'] = int(feature_dict[instance_name]['feature_num_vertices'])
        temp_list = []
        
        # Some other software should execute the code here, otherwise the certificates are expected to have the same name as their instance files and be stored in appropriate folders.
        filename = instance_name.replace(".col", ".sol") #changing file name to allow for matching in the subfolders.
        bestname = instance_name.replace(".col","")
        
        #if a best known solutions is known, add that as the "best algos" result, and update det best performance measure.
        if bestname in best_dict:
            algo_dict[instance_name]['best'] = int(best_dict[bestname]['best'])
            algo_dict[instance_name]['best_performance'] = int(best_dict[bestname]['best'])

        #looking for the subpaths that match the algorithms
        #   This assumes that the algorithm performances are stored in a folder with a name matching the algorithms.
        for algo in algos:
            algo_path = os.path.join("./Resources/results from GVC/", algo)
            
            if os.path.isdir(algo_path):
                #print(f"Checking for directory: {algo_path}")
                
                for subdir_name in os.listdir(algo_path):
                    subdir_path = os.path.join(algo_path, subdir_name)
                    #print(f"    Looking in {subdir_path} for {filename}")

                    if filename in os.listdir(subdir_path):
                        #print(f"Found file: {filename} in {subdir_path}") 
                    
                        f = open(os.path.join(subdir_path, filename), mode = "r") 
                        temp_list = []   
                        for line in f:
                            line = line.strip()  # Remove extra whitespace
                            temp_list.append(int(line))  # Convert to integer before adding
                        # get the set of all numbers in the file
                        temp_set = set(temp_list)
                        chromatic = len(temp_set)
                        algo_dict[instance_name]['best_performance'] = min(algo_dict[instance_name]['best_performance'], chromatic)
                        algo_dict[instance_name][algo] = chromatic
                        f.close()

                        break           # break here since we know only one solution pr instance pr algo folder                        
                    elif "_logs" in subdir_name:
                        pass
                    else:
                        print(f"File {filename} not found in {subdir_path}")
                        algo_dict[instance_name][algo] = float('nan')
            else:
                print(f"Algorithm directory {algo_path} does not exist")
                algo_dict[instance_name][algo] = float('nan')
        
        #adds the best solutions as the result of the "best algorithm" in case one wasnt known prior
        if bestname not in best_dict:
            algo_dict[instance_name]['best'] = algo_dict[instance_name]['best_performance']

    return algo_dict


#this needs a big update as it doesnt do what i want it to do.
#also needs to add some feature selection
def z_score_standardize(feature_dict):
    standardized_dict = {}

    feature_names = list(next(iter(feature_dict.values())).keys())
    #computing the mean and standard deviation for each feature 

    x = {
        feature: {
            "mean": np.mean([float(feature_dict[instance][feature]) for instance in feature_dict]),
            "std": np.std([float(feature_dict[instance][feature]) for instance in feature_dict])
        }
        for feature in feature_names
    }

    # applying the Z-score normalization
    for instance, features in feature_dict.items():
        #adding the instance to the new dict
        standardized_dict[instance] = {}
        for feature, value in features.items():
            if feature in x:
                mean = x[feature]['mean']
                std = x[feature]['std']
                if std > 0: # Ensures no division by zero
                    standardized_dict[instance][feature] = (float(value)- mean) / std
                else:
                    standardized_dict[instance][feature] = 0
            else:
                standardized_dict[instance][feature] = value

    return standardized_dict

def make_file(algos, path, filename, standardize = False): 
    # collect the dictionaries needed for file creation
    feature_dict = gather_features(path+'/InstanceFeatures.csv') # A static file that should be updated when a new instance is added.
    algo_dict = algo_performance(algos, feature_dict, path+'/best.csv')

    algo_best = algos+ ['best'] # grabs the best as to calculate the performance ratio later.

    # get the features and algorithms used to create a header for a CSV file.
    feature_names = list(next(iter(feature_dict.values())).keys()) # gets the headers dynamically.
    header = [feature for feature in feature_names]
    algorithms = ['algo_' + s for s in algo_best] 

    if standardize:
        feature_dict = z_score_standardize(feature_dict)
    
    with open(f"./isa/{filename}", mode="w", newline="") as file: # SHOULD UPDATE TO NO LONGET TAKE A FILENAME BUT AN ISA PATH INSTEAD
        writer = csv.writer(file)

        if filename == 'metadata.csv': 
        # write the headers on the first row, followed by the information from the dict on the following rows.
            writer.writerow(['instances', 'source'] + header + algorithms)
            iterator = 1 
            for instance_name, features in feature_dict.items():
                row = [
                    iterator,                                 # Indexing
                    instance_name                             # Instance name
                ] + list(features.values()) #dynamic addition of the features.

                # Generically adds the performances of the algorithms to the row.
                best_perf = algo_dict[instance_name]['best_performance']

                for algo in algo_best:
                    algo_perf = algo_dict[instance_name][algo]               
                    if best_perf != 0: # avoids division by zero
                        perf_ratio = (algo_perf - best_perf) / best_perf
                        #print(perf_ratio)
                    else: 
                        perf_ratio = float('nan')
                    row.append(perf_ratio)

                writer.writerow(row)
                iterator += 1    
            
        elif filename == 'data.csv':
            data_header = [col.removeprefix("feature_") for col in header]
            writer.writerow(data_header)
            for instance_name, features in feature_dict.items():
                row = list(features.values())
                writer.writerow(row)

    print(f"file: {filename} created")
    
# Have to update such that it takes a path and some algorithms as input.
    # figure out how this is done.
def test():
    timestamp = time.time()

    path = './Resources'
    algos = ['DSATUR', 'Greedy', 'RLF','HEA','TABUCOL'] 
    standardize = False
    
    make_file(algos, path, "data.csv")
    make_file(algos, path, "metadata.csv", standardize)

    end = time.time()
    print(end - timestamp)
    
    os.chdir("./isa")
    os.system("isa")

test()
#matilda_test_file()
'''
if __name__ == "__main__":
    #could for the page, just remove pyhard and instead only use pyispace, and then print the plots myself as i am already somewhat doing.
    parser = argparse.ArgumentParser(description=" This script takes a directory, a list of algorithms and a name for the outputfile, generating METADATA needed to perform ISA using pyhard")
    parser.add_argument("--dir", required=True, help="The directory containing the algorithm performance folder, and a file containing the features of the instances.")
    #could default to use all or simply the 5 thats been tested.
    parser.add_argument("--a", required=True, help="A list of algorithms to be used, names must correspond with the foldernames where the solution certificates are located, where a certificate must share a name with the instance it solves.")
    parser.add_argument("--o", required=True, help="Name of the output file")
'''