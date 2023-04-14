
rclone copy OneDrive:/Research/BugsBirth/Backup/Testeability/ManySStub4J/projects/$1-project.tar.gz projects/
tar -xf projects/$1-project.tar.gz
rm -rf projects/$1-project.tar.gz

rclone copy OneDrive:/Research/BugsBirth/Backup/Testeability/ManySStub4J/results/$1-results.tar.gz results/
tar -xf results/$1-results.tar.gz
rm -rf results/$1-results.tar.gz

# Extra

./scripts/runManySStub4JTestExperiment.sh $1

# docker run -it --rm -v $PWD:/home/jovyan/work/ -w /home/jovyan/work/ jupyter-bugs:v2 python3 notebooks/ProjectAnalysis/ProjectTestAnalysis.py $2