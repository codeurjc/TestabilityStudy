#!/bin/bash

if [ "$#" -ne 2 ]; then 
    echo "Use: ./scripts/backup.sh <DATASET> <PROJECT>"
    exit 1
fi

# Project
# echo "Saving project"
# mkdir -p tmp/projects/
# tar -czvf tmp/projects/$2-project.tar.gz projects/$2/ > /dev/null 2>&1
# rclone copy tmp/projects/$2-project.tar.gz OneDrive:/Research/BugsBirth/Backup/Testeability/$1/projects/
# rm -f tmp/projects/$2-project.tar.gz

# Result
echo "Saving results"
mkdir -p tmp/results/
tar -czvf tmp/results/$2-results.tar.gz results/$2/ > /dev/null 2>&1
#rclone copy tmp/results/$2-results.tar.gz OneDrive:/Research/BugsBirth/Backup/Testeability/$1/results/
#rclone copy tmp/results/$2-results.tar.gz OneDrive:/Research/BugsBirth/Backup/Testeability/$1/results_timeouts/
echo "Uploading to minio"
aws --endpoint-url https://minio.codeurjc.es s3 cp tmp/results/$2-results.tar.gz s3://michel/2023-JSEP-Testability/Diciembre-2022/
rm -f tmp/results/$2-results.tar.gz

# Pre-process results 
echo "Pre-process results"
docker run -it --rm -v $PWD:/home/jovyan/work/ -w /home/jovyan/work/ jupyter-bugs:v2 python3 notebooks/ProjectAnalysis/ProjectTestAnalysis.py $2

echo "Moving folders to tmp"
mv results/$2/ tmp/results/
#mv projects/$2/ tmp/projects/