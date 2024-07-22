# Reproducing open-projects software test execution experiment

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5425239.svg)](https://doi.org/10.5281/zenodo.5425239)

> This repository constitutes the reproduction package of the paper "Testing the past: can we still run tests in past snapshots for Java projects?" submitted to the Empirical Software Engineering journal (under review)

This package contains:

```bash
.
├── configFiles     # Config files for each project
├── dockerfiles     # Docker files for all necessary images to perform the experiment
├── notebooks       # Jupyter Notebooks for data extraction and analysis
├── previousResults # Results from previous studies
├── projects        # Subjects of the experiment (git repositories)
├── py              # Python scripts to perform the experiment
├── results         # Contains the results generate from the experiment
├── scripts         # Bash scripts to easy-perform the experiment
├── tmp             # Folder for temporary files
└── README.md 
```

In addition, the rest of this file describe methodological details of the studies presented in the work, and provides an introduction to the data:

<!-- vscode-markdown-toc -->
* [Set Up](#SetUp)
* [Step 1. Repository mining](#Step1.Repositorymining)
	* [1.1 Dataset selected](#Datasetselected)
	* [1.2 Project mining and selection](#Projectminingandselection)
		* [Many4J](#Many4J)
	* [1.3 How to reproduce this step](#Howtoreproducethisstep)
* [Step 2.Execution of the tests in the past](#Step2.Executionofthetestsinthepast)
	* [2.1 Experiment process](#Experimentprocess)
	* [2.3 How to reproduce this step](#Howtoreproducethisstep-1)
* [Step 3. Analysis of the results](#Step3.Analysisoftheresults)
	* [3.1 Preliminar Study](#PreliminarStudy)
	* [3.2 Create resume](#Createresume)
	* [3.3 Case Study](#CaseStudy)
	* [3.4 Experimental results](#Experimentalresults)
	* [3.5 Analyze results](#Analyzeresults)

Some data needed to correctly reproduce the experiment is hosted in Zenodo (https://zenodo.org/records/10069834), due to the limitations of the GitHub file size.
The dataset hosted in Zenodo contains the following files:

```bash

└── ManySStub4J (Many4J)          
    ├── ManySStub4J-projects.tar.gz # Repositories of each Many4J project (tar.gz)
    └── processed-results.tar.gz    # Procesed results per project (tar.gz)
```

##  Set Up

*Pre-requisites to reproduce our work*

- Git 2.17+
- Docker 19+

These dependencies will be needed to download this repository, build the Docker images and run the containers from those images.

# Conducting the experiment

The experiment was carried out in 3 phases:
- 1. Repository mining
- 2. Execution of the tests in the past
- 3. Analysis of the results

##  <a name='Step1.Repositorymining'></a>Step 1. Repository mining

###  <a name='Datasetselected'></a>1.1 Dataset selected

To carry out the experiment, we have selected a well-known dataset:

- **Many4J:** 100 projects selected from ManySStuBs4J dataset

###  <a name='Projectminingandselection'></a>1.2 Project mining and selection

####  <a name='Many4J'></a>Many4J

- Of the 100 original projects, 2 projects whose repository is no longer available, 1 project has not been included as it has not finished the execution of its experiment and 11 Android projects have been discarded. 
- Therefore, 86 projects have been selected

###  <a name='Howtoreproducethisstep'></a>1.3 How to reproduce this step

The execution of this step is implemented in a single Jupyter Notebook per dataset.

To reproduce this step:

- Build docker image Jupyter docker image locally
```
$ docker build -f dockerfiles/jupyter.Dockerfile -t jupyter-bugs .
```
- Run a docker container from this image (PWD should be root folder of the project)
```
$ docker run -d --rm --name jupyter-bugs -p 8888:8888 -v $PWD:/home/ -w /home/ jupyter-bugs
```
- [Open notebooks in browser](http://localhost:8888/tree/notebooks/ProjectsMining/)
- [Open notebooks in Gitlab/GitHub](notebooks/ProjectsMining/)

INPUT: 
- Info from Original Study projects: 
    - ManySStub4J: `previousResults/ManySStub4J/topJavaMavenProjects.csv`

OUTPUT: 
- Folder `configFiles/<dataset>Projects/` which contains all config files for next step
- All projects downloaded from GitHub at folder: `projects/`

> **Notes:**
> - Execute this experiment (download and analyze repositories) takes a considerable amount of time. 
> - If order to be able to reproduce the experiment, the following files and folders are provided:
>   - Git repositories for all datasets (available in [Zenodo dataset](https://zenodo.org/records/10069834))
>   - Config files at `configFiles/<dataset>/`

##  <a name='Step2.Executionofthetestsinthepast'></a>Step 2.Execution of the tests in the past

###  <a name='Experimentprocess'></a>2.1 Experiment process

From the configuration files generated in the previous step (Step 1), the defined commits/snapshots will be built iteratively for each project:

1. The repository is downloaded (if it does not available locally)
2. Inside the repository, it is placed in the commit you want to check
3. The build command for Maven is executed (mvn compile) inside a Docker container.
    - The success code (0 or not 0) and the log are collected 
4. The test build command for Maven is executed (mvn test-compile) inside a Docker container.
    - The success code (0 or not 0) and the log are collected
5. The test command for Maven is executed (mvn test) inside a Docker container.
    - The success code (0 or not 0) and the log are collected. All surefire-reports folders are also saved (contains results of the test in XML format)
6. Repeat steps 2-6 for the next commit.

##### Experiment Results

For each project, a results folder is generated in the `results/` folder which the following content:

- `build_files/` A JSON file is stored in this folder for each commit that collects the tested build settings and their result (whether it worked or not)
- `general_logs/` This folder contains a general log of the execution of the experiment. If this experiment was paused and resumed later, a new log is generated.
- `logs/` This folder stores a log for each build configuration executed on a snapshot. It includes 3 folders for each execution:
    - `logs/build`
    - `logs/build_test`
    - `logs/test`
- `test_results` This folder contains, for each commit where the tests have been executed, their results in XML format.
- `report_experiment.csv` This file contains the information of the results of the experiment. For each commit, it specifies whether it was successfully built or not, the execution time required by the build, and additional information about the snapshot, such as its creation date or the comment associated with the commit (See Table 1). 

*Table 1: Commit report example* 

| id | commit   | build   | build_exec_time | test_build | test_build_exec_time | test    | test_exec_time | date                      | comment |
|----|----------|---------|-----------------|------------|----------------------|---------|----------------|---------------------------|---------|
| 0  | a0defe57 | SUCCESS | 35              | SUCCESS    | 7                    | SUCCESS | 9              | 2014-09-23 15:11:35 +0800 | init    |

> **Notes:**
> The raw results (which include the logs of each phase of the experiment execution) have a size that exceeds the limits of platforms such as Zenodo (>1TB). If you need access to this raw data, please contact the following e-mail: michel.maes@urjc.es

###  <a name='Howtoreproducethisstep-1'></a>2.3 How to reproduce this step

To reproduce this step:

- Build docker image Jupyter docker image locally
```
$ docker build -f dockerfiles/build-analyzer.Dockerfile -t  build-analyzer:0.3.3-dev .
```
- Run a docker container from this image (PWD should be root folder of the project). You need to set _<project_name>_ (i.e. `jena`) and _<path_to_config_file>_ (i.e. `configFiles/ApacheProjects/isis-config.json`)
```
$ docker run -d --rm\
    -v $PWD/results:/home/bugs/results \
    -v $PWD/py:/home/bugs/py \
    -v $PWD/projects:/home/bugs/projects \
    -v $PWD/configFiles:/home/bugs/configFiles \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -w /home/bugs/ \
    --name build-experiment-<project_name> \
    --privileged=true \
    build-analyzer:0.3.3-dev python py/checkBuildHistory.py <path_to_config_file>
```

To make the execution easier, a bash script per dataset is provided to launch the experimentation of a project just from its name:

```
$ ./scripts/runManySStub4JTestExperiment.sh <project_name>
```

INPUT: 
- Configuration files from `configFiles/<dataset>Projects/`

OUTPUT: 
- Folders in `results/` per project as defined in section 2.2.

##  <a name='Step3.Analysisoftheresults'></a>Step 3. Analysis of the results

For this step you will need to have started a Docker container from the image built in step 1.3.

```
$ docker run -d --rm --name jupyter-bugs -p 8888:8888 -v $PWD:/home/ -w /home/ jupyter-bugs
```

###  <a name='PreliminarStudy'></a>3.1 Preliminar Study

We first conducted a preliminary study to explore the results obtained. 

- [Open notebooks in browser](http://localhost:8888/notebooks/notebooks/ProjectAnalysis/TestAnalysis/00-PreliminaryStudy.ipynb)
- [Open notebooks in Gitlab/GitHub](notebooks/ProjectAnalysis/TestAnalysis/00-PreliminaryStudy.ipynb)

The conclusion found is that out of 86 projects, only in 66 we were able to run at least 1 test.
This notebook also includes an exploratory study of the causes of test execution errors is carried out.

INPUT: 
- Raw data generated by Step 2

OUTPUT: 
- Folders in `notebooks/ProjectAnalysis/TestAnalysis/results` with the processed data.

> **Notes:**
> The output of this step is available in the repoducction package-data (https://zenodo.org/records/10069834) as `processed-results.tar.gz`.

###  <a name='Createresume'></a>3.2 Create resume

The amount of data generated forces us to generate a handy summary of the experiment. 
To do so, we will use a Jupyter Notebook that will collect the metrics set in the study.

- [Open notebooks in browser](http://localhost:8888/notebooks/notebooks/ProjectAnalysis/TestAnalysis/01-CreateResume.ipynb)
- [Open notebooks in Gitlab/GitHub](notebooks/ProjectAnalysis/TestAnalysis/01-CreateResume.ipynb)

INPUT: 
- Processed data generated by Step 3.1

OUTPUT: 
- Summaries of the results for each project, grouped by dataset: 
    - results/Many4JResults.csv

###  <a name='CaseStudy'></a>3.3 Case Study

In the following notebooks you will find all the data and graphs generated for the Case Study, where the metrics that measure how testable a project is are proposed.

INPUT: 
- Summaries of the results from Step 3.2

OUTPUT:
- Plots and tables for projects selected for the CaseStudy

###  <a name='Experimentalresults'></a>3.4 Experimental results

From the summaries obtained in step 3.2 we show metrics at dataset level as well as different plots of the projects.

- [Open notebooks in browser](http://localhost:8888/notebooks/notebooks/ProjectAnalysis/TestAnalysis/03-ExperimentalResults.ipynb)
- [Open notebooks in Gitlab/GitHub](notebooks/ProjectAnalysis/TestAnalysis/03-ExperimentalResults.ipynb)

INPUT: 
- Summaries of the results from Step 3.2

OUTPUT: 
- Graphics with project results
- Tables summarising the results

### <a name='Analyzeresults'></a>3.5 Analyze results

In this step, a more advanced analysis of the results is made, dividing them into quartiles according to different metrics and looking for the correlation of testability with these metrics. The results for the best projects for each of the testability flavours are also provided.

- [Open notebooks in browser](http://localhost:8888/notebooks/notebooks/ProjectAnalysis/TestAnalysis/04-AnalyzeResults.ipynb)
- [Open notebooks in Gitlab/GitHub](notebooks/ProjectAnalysis/TestAnalysis/04-AnalyzeResults.ipynb)

INPUT: 
- Summaries of the results from Step 3.2

OUTPUT: 
- Tables summarising the results by different metrics (Total commits, LoC or Age)
