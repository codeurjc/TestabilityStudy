#!/bin/bash

DATASET=$1

for result in results/*; do
    projectName=$(basename $result)
    if [ -d "$result" ] && [ ! -f "notebooks/ProjectAnalysis/TestAnalysis/results/$projectName/report.csv" ]
    then
        echo "Running backup for project ${projectName} ..."
        ./scripts/backup.sh $DATASET $projectName
        echo "> Backup finished for project ${projectName} ..."
    fi
done