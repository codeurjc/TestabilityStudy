#!/bin/bash

if [ "$#" -ne 2 ]; then 
    echo "Use: ./scripts/getLoc.sh <DATASET> <PROJECT>"
    exit 1
fi

# ./scripts/loc/getLoc.sh ManySStub4JProjects spring-cloud-microservice-example

docker run -d \
    --name loc-$2\
    -v $PWD:/home/jovyan/work/ \
    -w /home/jovyan/work/ jupyter-bugs:v2 \
    python notebooks/ProjectAnalysis/LoCAnalysis/LoCAnalysis.py configFiles/$1/$2-config.json
