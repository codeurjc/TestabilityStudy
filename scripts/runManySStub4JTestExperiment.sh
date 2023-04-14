#!/bin/bash

./scripts/runExperiment.sh configFiles/ManySStub4JProjects/$1-config.json $1

# i=1
# MAX=10
# for configFile in configFiles/ManySStub4JProjects/*; do
#     projectName=$(basename $configFile -config.json)

#     if [ ! -d "results/${projectName}" ] && [ ! -d "notebooks/ProjectAnalysis/TestAnalysis/results/${projectName}" ]
#     #if [ -d "results/${projectName}" ] # FOR RESTART CURRENT 
#     then
#         echo "${projectName} "
#         #./scripts/runExperiment.sh $configFile $projectName
#         ((i=i+1))
#         if [ $i -gt $MAX ] 
#         then
#             exit
#         fi
#     fi
    
# done