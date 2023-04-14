import csv
import pandas as pd
import re
import hashlib
import os
import json
import subprocess
import sys

HEADERS = ["INDEX","COMMIT_ID","IS_MAVEN","OLD_BUILD_SUCCESSFUL", "NEW_BUILD_SUCCESSFUL", "OLD_EXCEPTION", "NEW_EXCEPTION"]

class LogAnalyzer:
    

    def __init__(self, project_name, root="/home/jovyan/work", experiment=2):
        self.root = root
        self.project = project_name
        self.results_path= "%s/results/%s/experiment_%d"%(root, project_name, experiment)
        report="%s/report_experiment_%d.csv"%(self.results_path, experiment)
        data= pd.read_csv(report)
        self.csvList = dict()
        with open(report) as csvfile:
            reader = csv.DictReader(csvfile)
            for idx, row in enumerate(reader):
                self.csvList[idx] = row

        self.maven_common_errors = dict()
        reader = csv.reader(open('%s/previousResults/TufanoResults/maven-common-errors.txt'%root, "r"))
        for row in reader:
            k, v = row
            self.maven_common_errors[k] = v
    
    def get_build_file(self, idx, commit_hash):
        build_file_path=self.results_path+"/build_files/%d-%s-build.json"%(idx, commit_hash)
        with open(build_file_path) as f: 
            data = json.load(f)
            return data

    def get_maven_errors(self, log_path):
        exceptions = []
        causes = []
        log = subprocess.check_output(['cat',log_path])
        for exception in self.maven_common_errors.keys():
            if exception in str(log):
                exceptions.append(exception)
                causes.append(self.maven_common_errors[exception])
        main_cause = causes[-1]
        return exceptions, main_cause

    def analyze(self):

        results = {}

        result_path = "%s/notebooks/ProjectAnalysis/TestAnalysis/results/%s/build-test-errors.json" % (self.root, self.project)

        if os.path.exists(result_path):
            print("> Project %s already analyzed"%self.project)
            #return

        for result in self.csvList.values():
            
            src_build = None
            test_build = None

            if result['build'] == "FAIL":

                build_file = self.get_build_file(int(result['id']), result['commit'])
                hasBuildSystem = build_file['build_system'] == "Maven"
                
                if hasBuildSystem:

                    if int(result['build_exec_time']) >= 300:
                        src_exceptions = ["Timeout"]
                        src_main_cause = "Resolution"
                    else:
                        # Only Maven log
                        log_path = "%s-%s-attempt-1.log" % (result['id'], result['commit'])
                        src_build_exceptions, src_build_main_cause = self.get_maven_errors(self.results_path+'/logs/build/'+log_path)
                else:
                    src_build_exceptions = ["NO BUILD SYSTEM"]
                    src_build_main_cause = "NO BUILD SYSTEM"
                
                src_build = {
                    "exceptions": src_build_exceptions,
                    "main_cause": src_build_main_cause
                }
            else: # BUILD WORKS

                hasBuildSystem = True

                if result['test_build'] == "FAIL":

                    if int(result['test_build_exec_time']) >= 300:
                            test_build_exceptions = ["Timeout"]
                            test_build_main_cause = "Resolution"
                    else:
                        # Only Maven log
                        log_path = "%s-%s-build.log" % (result['id'], result['commit'])
                        test_build_exceptions, test_build_main_cause = self.get_maven_errors(self.results_path+'/logs/build_test/'+log_path)
                    
                    test_build = {
                        "exceptions": test_build_exceptions,
                        "main_cause": test_build_main_cause
                    }

                # else: # TEST BUILD WORKS

            results[result['commit']] = {
                "hasBuildSystem": hasBuildSystem,
                "src_build": src_build,
                "test_build":test_build
            }

        with open(result_path, 'w') as fp:
            json.dump(results, fp)

if __name__ == "__main__":
    la = LogAnalyzer(sys.argv[1])
    la.analyze()
