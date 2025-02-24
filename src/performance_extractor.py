import os
import os.path
import csv
import time
#import argparse

##
# The following script assumes only valid solutions are present in the directories that it gathers performances from.
#   If an invalid solution is present that it will be treated as valid, thus the validation and removal should be handled by a seperate script used upon posting of a solution.
##
def gather_algo_performance(results_dir, feature_dict_path, best_solutions_path, output_csv):
    print("Processing Algorithm results...")
    
    algo_dict = {}
    best_dict = {}
    
    # Load best known solutions
    ## Might want to update this to be a static path directing to the markdown containing the best solutions instead.
    with open(best_solutions_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = row['Source']
            row.pop('Source')
            best_dict[key] = row
    
    # Load feature dictionary
    feature_dict = {}
    with open(feature_dict_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            feature_dict[row['feature_source']] = row
    
    # Identify available algorithms by scanning the directory
    algos = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
    
    for instance_name in feature_dict:
        algo_dict[instance_name] = {}
        algo_dict[instance_name]['best_performance'] = int(feature_dict[instance_name]['feature_num_vertices'])
        bestname = instance_name.replace(".col", "")
        filename = instance_name.replace(".col", ".sol")
        
        if bestname in best_dict:
            algo_dict[instance_name]['best'] = int(best_dict[bestname]['best'])
            algo_dict[instance_name]['best_performance'] = int(best_dict[bestname]['best'])
        
        for algo in algos:
            algo_path = os.path.join(results_dir, algo)
            
            for subdir_name in os.listdir(algo_path):
                subdir_path = os.path.join(algo_path, subdir_name)
                
                if os.path.isdir(subdir_path) and filename in os.listdir(subdir_path):
                    with open(os.path.join(subdir_path, filename), mode="r") as f:
                        colors = {int(line.strip()) for line in f}
                        chromatic = len(colors)
                        algo_dict[instance_name]['best_performance'] = min(algo_dict[instance_name]['best_performance'], chromatic)
                        algo_dict[instance_name][algo] = chromatic
                    break
                else:
                    algo_dict[instance_name][algo] = float('nan')
        
        if bestname not in best_dict:
            algo_dict[instance_name]['best'] = algo_dict[instance_name]['best_performance']
    
    # Write output to CSV 
    # Should probably remove best_performance here since it makes more sense to handle based on the individual metadatafiles as opposed to based on all the algorithms
    # that may or may not be tested already, in the long run it should become obsolete anyways
    fieldnames = ['instance_name', 'best', 'best_performance'] + algos
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for instance, data in algo_dict.items():
            row = {'instance_name': instance, **data}
            writer.writerow(row)
    
    print(f"Results saved to {output_csv}")

def test():
    start = time.time()
    result_dir = "./Resources/results from GVC"
    feature_path = "./Resources/InstanceFeatures.csv" # this value could remain static.
    best_solutions = "./Resources/best.csv"           # Could be changed to the markdown 
    output = "./Resources/algoPerf.csv"
    gather_algo_performance(result_dir, feature_path, best_solutions, output)

    end = time.time()
    print(end-start)

test() # might be fine for now, could have this remain like this, and just be completely static..

'''
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gather algorithm performance results.")
    parser.add_argument("--results_dir", required=True, help="Path to the directory containing algorithm results.")
    parser.add_argument("--feature_dict", required=True, help="Path to the feature dictionary CSV file.")
    parser.add_argument("--best_solutions", required=True, help="Path to the best known solutions CSV file.")
    parser.add_argument("--output_csv", required=True, help="Path to the output CSV file.")
    
    args = parser.parse_args()
    gather_algo_performance(args.results_dir, args.feature_dict, args.best_solutions, args.output_csv)
'''