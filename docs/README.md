This is the inital starting page of the github pages site:

From here you can follow this link: [Example html](./example/page.html)
The linked paged shows the plot of an Instance space analysis using the instances present in the directory, and testing/comparing the performance of Greedy construction, DSATUR construction, RLF construction, TABUCOL and HEA.
    Where the coloring of the graph can be changed such that different features can be viewed.

New Instance Space Analysis(ISA), can be triggered by modifying the config.yaml file found in the primary directory of the repository, chosing which algorithms and setting parameters, pushing this modified config to the repo will trigger a github action that will run the ISA and generate a page similar to the example.

All Algorithms have currently been run for a maximum of 10 minutes. Therefore for a fair comparison with new algorithms they are expected to have had a similar limit on their allowed running time.

To Trigger an Instance Space Analysis, one should modify the config.yaml found in the main directory of the repo, and push those changes. depending on the number of instances uses, the time to complete this task will vary.

TODO:
    Make a small getting started page that explains how to use the repo to generate the ISA and associated page in a more clear and descriptive way.