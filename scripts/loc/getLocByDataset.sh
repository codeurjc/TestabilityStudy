for configFilePath in configFiles/$1Projects/*; do

    projectName=$(basename $configFilePath -config.json)

    if [ -d "projects/${projectName}" ] && [ -d "notebooks/ProjectAnalysis/TestAnalysis/results/${projectName}" ]
    then
       echo "${projectName}"
       docker run -d \
        --name loc-${projectName} \
        -v $PWD:/home/jovyan/work/ \
        -w /home/jovyan/work/ jupyter-bugs:v2 \
        python notebooks/ProjectAnalysis/LoCAnalysis/LoCAnalysis.py $configFilePath
    fi
    
done