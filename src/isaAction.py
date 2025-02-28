import os
import argparse
import yaml # used for the config.yaml file that will need to be updated to trigger an ISA.
import json # for creating the options.json file 

def create_subdirs(dir_name):
    os.makedirs(f"../analysis/{dir_name}")
    print("Analysis directory created")
    # create the option file based on a config
    algos = read_config(dir_name) # could probably move this out from here but its not needed atm
    
    os.makedirs(f"../docs/{dir_name}")
    print("Pages directory created")
    
    with open(f"../docs/{dir_name}/page.html", mode = 'rb') as src_file:
        with open(f"../docs/{dir_name}/page.html", mode= "wb") as dest_file:
            # reading and writing chunks at a time
            dest_file.write(src_file.read())

    print(f"Page.html copied to: ../docs/{dir_name}")
    return algos

def read_config(dir_name):
    with open('../config.yaml', 'r') as file:
        config = yaml.safe_load(file) # reads the file 

    algorithms = config.get('algos', []) # saving algos parsing to the databuilder
    
    config.pop('algos', None) # removing algos as its the only field not pertaining to the options file

    with open(f'../analysis/{dir_name}/options.json', mode = 'w') as json_file:
        json.dump(config, json_file, indent=4)

    print("Options File created saved")
    return algorithms

def run(dir_name):
    algos = create_subdirs(dir_name)
    os.system(f"python dataBuilder_bestAsAlgo.py --a {algos} --o ./analysis/{dir_name}")
    os.chdir(f"../analysis/{dir_name}")
    os.system("isa")
    os.chdir("../../src")
    os.system(f"python coordinateBuilder.py --input ../analysis/{dir_name} --o ../docs/{dir_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="triggers ISA")
    parser.add_argument("--dir", required=True, help= "A name for the specified directory")
    args = parser.parse_args()
    run(args.dir)
