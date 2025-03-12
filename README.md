# GVC-validator
Github project, which utilized github actions to update best known solutions for instances, and trigger Instance Space Analysis (ISA) creating a simple ploting that allows for comparison and exploration. 

The current validation is done using a simple python script.
It should be possible to update the checker to use the coloring verifier made by Marco Chiarandini using the github actions to not only compile the code, but also execute it similarly to how the current checker is used.

All Algorithms have currently been run for a maximum of 10 minutes. Therefore for a fair comparison with new algorithms they are expected to have had a similar limit on their allowed running time.

To Trigger an Instance Space Analysis, one should modify the config.yaml found in the main directory of the repo, and push those changes. depending on the number of instances uses, the time to complete this task will vary.