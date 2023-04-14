docker run -d \
    --name log-analyzer-$1 \
    -v $PWD:/home/jovyan/work/ \
    -w /home/jovyan/work/ \
    jupyter-bugs:v2 python notebooks/ProjectAnalysis/LogAnalyzer.py $1