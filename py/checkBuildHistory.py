# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import datetime
import time
import csv
import json
import pickle
import json

from Project import Project
from JavaBuildHelper import JavaBuildHelper
from utils import DockerManager
from JavaTestHelper import JavaTestHelper

class BuildChecker():

    def __init__(self, config_file_path, test=False):

        self.test = test

        self.project = Project(config_file_path)
        
        self.docker_manager = DockerManager(self.project.getProcessManager())
       
    def checkCommitHistory(self):

        self.project.log("CHECK BUILD FOR EXPERIMENT %d" % self.project.config['experiment'])
        # MOVE TO PROJECT
        self.project.goToProjectFolder()

        count = 0
        total = self.project.getNumberOfCommits()
        build_config = None
        for c_hash, commit in self.project.report.getRows():

            count = count + 1

            self.project.log("%s commit gona be checked" % c_hash)

            time_out_reached = int(commit['build_exec_time']) >= 300 or int(commit['test_build_exec_time']) >= 300 or int(commit['test_exec_time']) >= 300

            already_checked = commit['build'] != "NO" and not time_out_reached

            # CHECK BUILD

            build_config = self.checkBuild(c_hash, commit, already_checked)

            # CHECK TEST COMPILE

            if commit['build'] == "SUCCESS" and not already_checked:
                    
                testHelper = JavaTestHelper(self.project.getProcessManager())
                # COMPILE TEST
                start = round(time.time()) 
                testsCompileSuccessFully = testHelper.compileTest(
                    self.project.config["project"],
                    self.docker_manager, 
                    build_config, 
                    # PATH WHERE LOG WILL BE STORE
                    self.project.build_test_logs_path+str(commit['id'])+"-"+c_hash+"-build.log"
                )
                delta_time = round(time.time()) - start

                commit['test_build'] = "SUCCESS" if testsCompileSuccessFully == 0 else "FAIL"
                commit['test_build_exec_time'] = delta_time
                
                if testsCompileSuccessFully == 0:

                    # RUN TEST
                    start = round(time.time())
                    testsRunSuccessFully = testHelper.runAllTest(
                        self.project.config["project"],
                        self.docker_manager, 
                        build_config, 
                        # PATH WHERE LOG WILL BE STORE
                        self.project.test_logs_path+str(commit['id'])+"-"+c_hash+"-test.log"
                    )
                    delta_time = round(time.time()) - start

                    testHelper.saveSurefireReports(self.project, str(commit['id'])+"-"+c_hash)

                    commit['test'] = "SUCCESS" if testsRunSuccessFully == 0 else "FAIL"
                    commit['test_exec_time'] = delta_time
            
            if not already_checked:
                self.project.report.updateReport()

            if not self.test:
                print("Builds checked : "+str(count)+"/"+str(total), end="\r")
    
    def checkBuild(self, c_hash, commit, already_checked):
        if not already_checked: 

                # GO TO  COMMIT
                self.project.change_commit(c_hash)

                # BUILD SNAPSHOT / COMMIT

                build_config = self.buildProject(c_hash, commit, self.project.config.get('build_config'))

                # SAVE BUILD FILE

                self.saveBuildFile(commit, c_hash, build_config)

                return build_config
            
        else: # BUILD CHECKED
            
            if commit['build'] == "SUCCESS":
                self.project.log("%s commit already checked: SUCCESS" % c_hash)
            if commit['build'] == "FAIL":
                self.project.log("%s commit already checked: FAIL" % c_hash)
            
            # GET SAVED BUILD CONFIG
            filename = str(commit['id'])+"-"+c_hash+"-build.json"

            build_config = None
            with open(self.project.build_files_path+filename,'r+') as json_file:
                build_config = json.load(json_file)
            return build_config

    def buildProject(self, c_hash, commit, default_build_config):

        if default_build_config:
            # USE DEFAULT CONFIG
            build_configs = [default_build_config]
        else:
            # DETECT BUILD CONFIG
            buildHelper = JavaBuildHelper(self.project.getProcessManager())
            build_configs = buildHelper.getBuildConfigs(default_build_config)
        
        delta_time = 0

        # TRY DIFFERENT BUILDS

        for idx, bc in enumerate(build_configs):
            
            start = round(time.time())
            # Start build
            exit_code = buildHelper.executeBuildSystem(
                self.project.config["project"],
                self.docker_manager, 
                bc, 
                # PATH WHERE LOG WILL BE STORE
                self.project.build_logs_path+str(commit['id'])+"-"+c_hash+"-attempt-"+str(idx+1)+".log"
            )
            # End build
            delta_time = round(time.time()) - start

            if exit_code == 0:
                # SUCCESS
                self.project.log("%s commit build success" % c_hash)
                commit['build'] = "SUCCESS"
                commit['build_exec_time'] = delta_time
                bc["works"] = True
                bc = bc.copy()
                bc["builds_checked"] = build_configs
                return bc
        
        # NO BUILD WORKS 
        self.project.log("%s commit build fail" % c_hash)
        commit['build'] = "FAIL"
        commit['build_exec_time'] = delta_time
        # RETURN FIRST BUILD CONFIG DETECTED, RETURN ALL BUILDS AS A PARAM
        bc = build_configs[0].copy()
        bc["builds_checked"] = build_configs
        return bc    

    def saveBuildFile(self, commit, c_hash, build_config):
        filename = str(commit['id'])+"-"+c_hash+"-build.json"
        with open(self.project.build_files_path+filename,'w+') as json_file:
            data = {
                "commit": c_hash,
                "build_system": build_config["build_system"],
                "docker_image": build_config["docker_image"],
                "build_command": build_config["build_command"],
                "build_file": build_config["build_file"],
                "builds_checked": build_config["builds_checked"],
                "works": commit['build'] == "SUCCESS"
            }
            json.dump(data, json_file, indent=4)

    
    def finish(self, msg):
        # RESTORE STATE AND CLOSE FILES
        self.project.log(msg)
        self.docker_manager.shutdownContainers()
        
        # CLOSE PROJECT
        self.project.close()

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Use: python py/checkBuildHistory.py <config_file_path>")
        exit()

    bcheck = BuildChecker(sys.argv[1])

    try:
        bcheck.checkCommitHistory()
    except KeyboardInterrupt as e:
        bcheck.finish("FINISHED EXPERIMENT WITH KeyboardInterrupt")
    except Exception as e:
        bcheck.project.log("Exception: %s"%e)
        bcheck.finish("FINISHED EXPERIMENT WITH AN EXCEPTION")
    else:
        bcheck.finish("FINISHED EXPERIMENT SUCCESSFULLY")


