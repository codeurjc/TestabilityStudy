import sys
import json
import os
import csv
import pandas as pd

from loc import calculateLOC

ROOT = "/home/jovyan/work/"
sys.path.append(ROOT+"py/")

DELIMITER="|=|"

from Report import Report
from GitManager import GitManager

def addLoCToReport(config_file_path):

    config = {}

    with open(config_file_path) as config_file:
        config = json.load(config_file)

    project_path = "%s/projects/%s/" % (ROOT,config['project'])

    gm = GitManager(project_path,config['last_commit'])

    report = Report("%s/notebooks/ProjectAnalysis/TestAnalysis/results/%s/report.csv" % (ROOT, config['project']))

    loc_path = "%s/notebooks/ProjectAnalysis/TestAnalysis/results/%s/loc.csv" % (ROOT, config['project'])
    if not os.path.exists(loc_path):
        commits = []
        for c_hash, commit in report.getRows():
            commits.append({
                'id': commit['id'],
                'commit': c_hash,
                'files': "",
                'loc': "",
                'test_files': "",
                'test_loc': "",
            })
        df = pd.DataFrame.from_records(commits)
        df.to_csv(loc_path, index=False)
    
    loc_report = pd.read_csv(loc_path)

    for i in loc_report.index:

        if not pd.isnull(loc_report.loc[i, 'files']):
            print("Skip %s"%i)
            pass
        else:
            print("Analyzing %s"%i)
            gm.change_commit(loc_report.loc[i, 'commit'])
            files, loc = calculateLOC(project_path,"Java","**/*.java")
            loc_report.at[i,'files'] = files
            loc_report.at[i,'loc'] = loc
            test_files, test_loc = calculateLOC(project_path,"Java","**/*Test*.java")
            loc_report.at[i,'test_files'] = test_files
            loc_report.at[i,'test_loc'] = test_loc
            loc_report.round().to_csv(loc_path, index=False)
    
    print("Finish ")


if __name__ == "__main__":
    print(sys.argv[1])
    
    # python notebooks/ProjectAnalysis/LoCAnalysis/LoCAnalysis.py configFiles/ManySStub4JProjects/spring-cloud-microservice-example-config.json
    addLoCToReport(sys.argv[1])