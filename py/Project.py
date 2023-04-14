from utils import ProcessManager, GitManager, DELIMITER
import os
import json
from time import gmtime, strftime
from Report import Report

class Project():

    def __init__(self, config_file_path):

        with open(config_file_path) as config_file:
            self.config = json.load(config_file)
        self.config['experiment'] = int(self.config['experiment'])
        self.config['last_commit'] = self.config['last_commit']
        # PATHS
        self.root = os.getcwd()
        self.path = '%s/results/%s/experiment_%s/'%(self.root, self.config['project'], self.config['experiment'])
        self.build_files_path = "%s/build_files/"%(self.path)
        self.build_logs_path = "%s/logs/build/"%(self.path)
        self.build_test_logs_path = "%s/logs/build_test/"%(self.path)
        self.test_logs_path = "%s/logs/test/"%(self.path)
        self.test_results_path = "%s/test_results/"%(self.path)
        self.general_logs_path = "%s/general_logs/"%(self.path)
        self.out_report = "%s/report_experiment_%d.csv"%(self.path,self.config['experiment'])
        self.project_folder = "projects/%s" % self.config['project']

        self._downloadRepoIfNotExist()
        self._makeResultsDirIfNotExist()

        self.process_manager = ProcessManager(open(self.general_logs_path+"general-"+strftime("%d%b%Y_%X", gmtime())+".log", 'w+'), "BUILD CHECKER")
        self.git_manager = GitManager(self.process_manager, self.config['last_commit'])

        if os.path.exists(self.out_report):
            # LOAD PREVIOUS REPORT
            self.report = Report(self.out_report)
        else:
            rawCommits = []
            # CREATE NEW REPORT
            if 'commits' in self.config:
                # USING CERTAIN COMMITS
                rawCommits = [(commit["c_hash"], commit['date'], commit['comment']) for commit in self.config['commits']]
            else:
                # USING ALL COMMITS ON GIT (MASTER BRANCH)
                self.goToProjectFolder()
                rawCommits = [ commit.split(DELIMITER) for commit in self.git_manager.getAllCommits()]
                os.chdir(self.root)

            self.report = Report(self.out_report, rawCommits=rawCommits, reportExist=False)

    def getProcessManager(self):
        return self.process_manager
    
    def getGitManager(self):
        return self.git_manager
    
    def goToProjectFolder(self):
        os.chdir(self.project_folder)

    def log(self, text):
        self.process_manager.log(text)

    def change_commit(self, commit_hash):
        self.git_manager.change_commit(commit_hash)

    def getNumberOfCommits(self):
        if not 'number_of_builds' in self.config or self.config['number_of_builds'] == "All":
            return len(self.report.getRows())
        else:
            return self.config['number_of_builds']

    def close(self):
        self.getProcessManager().execute("chmod -R ugo+rw %s/results/"%self.root)
        self.process_manager.close()
        os.chdir(self.root)

    # PRIVATE

    def _downloadRepoIfNotExist(self):
        # GET PROYECT (IF NOT EXIST IN LOCAL FOLDER /projects)
        if not os.path.isdir(self.project_folder):
            if not 'git_url' in self.config:
                raise Exception("Project does not exist and 'git_url' param not provided in config file")
            else:
                print("Project '%s' not available locally. Downloading ..."%self.config['project'])
                ProcessManager.default_exec("git clone %s %s"%(self.config['git_url'], self.project_folder))

    def _makeResultsDirIfNotExist(self):
        if not os.path.isdir(self.path):
            # FIRST EXECUTION
            os.makedirs(self.build_logs_path)
            os.makedirs(self.test_logs_path)
            os.makedirs(self.general_logs_path)
            os.makedirs(self.build_files_path)
            os.makedirs(self.build_test_logs_path)
            os.makedirs(self.test_results_path)
            
