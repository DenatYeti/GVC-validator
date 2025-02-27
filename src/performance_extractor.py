import os
import os.path
import csv
import time

def get_best(best_solutions_path):
    best_dict = {}

    with open(best_solutions_path, mode='r', encoding = 'utf-8') as file:
        lines = file.readlines()

    table_lines = [line.strip() for line in lines if line.strip().startswith("|")]

    if not table_lines:
        print("No markdown table found in the specified file.")
    else: 
        # first row should be the header
        header = [col.strip() for col in table_lines[0].strip("|").split("|")]

        #skipping the second row as the format means that it is a separator row
        for row_line in table_lines[2:]:
            row_data = [cell.strip() for cell in row_line.strip("|").split("|")]

            #skips any incomplete rows. in case a manual row was made wrong
            if len(row_data) != len(header):
                continue
            
            #creates a mapping for each header to its corresponding cell
            row = dict(zip(header, row_data))
            key = row.pop("Instance")
            best_dict[key] = row
            
    return best_dict
##
# The following script assumes only valid solutions are present in the directories that it gathers performances from.
#   If an invalid solution is present that it will be treated as valid, thus the validation and removal should be handled by a seperate script used upon posting of a solution.
##
def gather_algo_performance(results_dir, feature_dict_path, best_solutions_path, output_csv):
    print("Processing Algorithm results...")
    
    algo_dict = {}
    
    # Load best known solutions
    best_dict = get_best(best_solutions_path)
    
    # Load feature dictionary
    feature_dict = {}
    with open(feature_dict_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            feature_dict[row['feature_source']] = row
    
    # Identify available algorithms by scanning the directory
    algos = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]

    existing_algos = set()
    if os.path.exists(output_csv):
        with open(output_csv, mode= 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                instance_name= row['instance_name']
                algo_dict[instance_name] = {key: (int(value) if value.isdigit() else value) for key, value in row.items() if key != 'instance_name'}
                existing_algos.update(row.keys())
    
    for instance_name in feature_dict:
        if instance_name not in algo_dict:
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
    
    all_algos = sorted(existing_algos.union(algos))

    # Write output to CSV 
    # Should probably remove best_performance here since it makes more sense to handle based on the individual metadatafiles as opposed to based on all the algorithms
    # that may or may not be tested already, in the long run it should become obsolete anyways
    fieldnames = ['instance_name', 'best', 'best_performance'] + all_algos
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for instance, data in algo_dict.items():
            row = {'instance_name': instance, **data}
            writer.writerow(row)
    
    print(f"Results saved to {output_csv}")

def run():
    start = time.time()
    result_dir = "../Resources/solutions"  
    feature_path = "../Resources/InstanceFeatures.csv" # this value could remain static.
    best_solutions = "../best_solutions.md" 
    output = "../Resources/algoPerf.csv"
    gather_algo_performance(result_dir, feature_path, best_solutions, output)

    end = time.time()
    print(end-start)

run() # might be fine for now, could have this remain like this, and just be completely static..

