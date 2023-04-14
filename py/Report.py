import csv
import os

class Report():

    HEADERS = ["id", "commit", "build", "build_exec_time", "test_build","test_build_exec_time","test","test_exec_time", "date", "comment"]

    def __init__(self, out_report_path, rawCommits=[], reportExist=True):
        self.out_report_path = out_report_path
        self.csvDict = dict()

        if not reportExist:
            self._generateNewReport(rawCommits)

        self._loadResult()
        

    def _generateNewReport(self, rawCommits):
        # GO PROJECT FOLDER
        # os.chdir(self.project_folder)
        with open(self.out_report_path, 'w+') as csvfile: 
            writer = csv.DictWriter(csvfile, fieldnames = self.HEADERS) 
            commits = []
            n=0
            for commit in rawCommits:
                if len(commit) != 3: continue # This line prevents from errors due to strange format of comment
                commit_hash, date, comment = commit
                commits.append({
                    "id": n,
                    "commit": commit_hash,
                    "build": "NO",
                    "build_exec_time": 0,
                    "test_build": "NO",
                    "test_build_exec_time": 0,
                    "test": "NO",
                    "test_exec_time": 0,
                    "date": date,
                    "comment": comment
                })
                n+=1
            writer.writeheader()
            writer.writerows(commits)
    
    def _loadResult(self):
        # READ LAST REPORT
        with open(self.out_report_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.csvDict[row['commit']] = row
            # SORT ITEMS BY ID (DON'T NEED IT IN PYTHON 3.6)
            self.csvItems = sorted(self.csvDict.items(), key=lambda tup: int(tup[1]['id']) )

    def updateReport(self, headers=HEADERS):
        with open(self.out_report_path, 'w+') as csvfile: 
            writer = csv.DictWriter(csvfile, fieldnames = headers) 
            writer.writeheader()
            for _, commit in self.csvItems:
                writer.writerow(commit)   

    def getRows(self):
        return self.csvItems


    