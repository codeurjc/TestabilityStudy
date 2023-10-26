
# coding: utf-8

import csv
import pandas as pd
import matplotlib.pyplot as plt
import re
import hashlib
import numpy as np
import pickle
from matplotlib import rc
import os
import json
from ProjectAnalysis import ProjectAnalysis
from junitparser import JUnitXml, Failure, Error, Skipped
from collections import Counter
import sys
import shutil
from statistics import median, mean
from datetime import datetime, timezone
import dateparser

# Turn interactive plotting off
plt.ioff()

class ProjectTestAnalysis():

    def __init__(self, project, n, root="/home/jovyan/work", forceGenerate=False):
        self.project = project
        self.n = n
        self.root = root
        self.results_path = self.root + "/notebooks/ProjectAnalysis/TestAnalysis/results/" + self.project
        self._generateProcessedResults(forceGenerate=forceGenerate)

    def countWords(self, array):
        counter_array = []
        for t in Counter(array).items():
            word = t[0]
            count = t[1]
            counter_array.append((word,count))
        return counter_array

    def getSummary(self, forceGenerate=False):

        if not 'n_days' in self.summary.columns:

            report = self.getReport()

            delta_days = []

            for _, row in report.iterrows():
                now = datetime(2021, 7, 1, tzinfo=timezone.utc)
                original = dateparser.parse(row['date']).replace(tzinfo=timezone.utc)
                delta = now-original
                delta_days.append(delta.days)

            self.summary['n_days'] = delta_days
            self.summary.to_csv(self.results_path + "/summary.csv", index=False)

        if True or not 'testable_rate' in self.summary.columns:

            testable_rate_list = []

            for _, row in self.summary.iterrows():
                if row['n_test'] > 0:
                    testable_rate = (row['n_success']) / (row['n_test'])
                    testable_rate_list.append(testable_rate)
                else:
                    testable_rate_list.append(0)

            self.summary['testable_rate'] = testable_rate_list
            self.summary.to_csv(self.results_path + "/summary.csv", index=False)

        return self.summary

    def getFailures(self, forceGenerate=False):
        return self.failures_df

    def getErrors(self, forceGenerate=False):
        return self.error_df
    
    def getTestCasesRank(self, forceGenerate=False):
        return self.test_case_df

    def getReport(self):
        return self.report

    def getLoCReport(self):
        return self.loc_report

    def getMeanAndMedianOfConsecutiveFails(self):
        consecutive_fails_per_commit = []
        consecutive_fails = 0
        for idx, commit in self.report.iterrows():
            if commit['build'] == 'FAIL':
                consecutive_fails += 1
                consecutive_fails_per_commit.append(consecutive_fails)
            else:
                consecutive_fails = 0
                consecutive_fails_per_commit.append(consecutive_fails)
        return mean(consecutive_fails_per_commit), median(consecutive_fails_per_commit)

    def map_commit(self, row):
        return self.loc_report.iloc[row.id]['test_loc']

    def map_commit2(self, row):
        return self.loc_report.iloc[row.id]['loc']

    def generateAndSavePlot(self):
        color_map = {
            'n_success': 'lightgreen',
            'n_failures': 'red',
            'n_errors': 'orange',
            'test_loc': 'purple',
            'loc': 'dodgerblue',
        }
        
        results_df = self.getSummary()

        results_df['test_loc'] = results_df.apply(self.map_commit, axis=1)
        results_df['loc'] = results_df.apply(self.map_commit2, axis=1)

        ax = (
            results_df
            [['id','n_failures','n_errors','n_success']]
            .set_index('id').plot.area(title=self.project, color=color_map)
        )

        plt.ylabel("Number of test")

        results_df[['id','test_loc', 'loc']].set_index('id').plot.line(title=self.project, ax=ax, secondary_y=True,  color=color_map)

        plt.ylabel("LoC")
        plt.xlabel("Commits")

        fig = ax.get_figure()
        fig.savefig(self.results_path+"/test-chart.pdf")
        plt.show()


    def _generateProcessedResults(self, forceGenerate=False):

        report_path          = self.results_path+"/report.csv"
        summary_path         = self.results_path+"/summary.csv"
        failures_count_path  = self.results_path+"/failures_count.csv"
        errors_count_path    = self.results_path+"/errors_count.csv"
        test_cases_rank_path = self.results_path+"/test_cases_rank.csv"
        loc_report_path      = self.results_path+"/loc.csv"

        if not forceGenerate and os.path.isdir(self.results_path):

            # RESTORE  (GENERATE SUMMARY IS TIME-CONSUMING)

            self.report= pd.read_csv(report_path)
            self.summary = pd.read_csv(summary_path)
            self.failures_df = pd.read_csv(failures_count_path) if os.path.isfile(failures_count_path) else None
            self.error_df = pd.read_csv(errors_count_path) if os.path.isfile(errors_count_path) else None
            self.test_case_df = pd.read_csv(test_cases_rank_path) if os.path.isfile(test_cases_rank_path) else None
            self.loc_report = pd.read_csv(loc_report_path) if os.path.isfile(loc_report_path) else None
            
        else: 

            if not os.path.isdir(self.results_path):
                os.makedirs(self.results_path)

            # SAVE A COPY OF REPORT
            shutil.copyfile("%s/results/%s/experiment_%d/report_experiment_%d.csv"%(self.root, self.project, self.n, self.n), report_path)
            self.report = pd.read_csv(report_path)

            # GENERATE SUMMARY

            pa = ProjectAnalysis(self.project, self.n, self.root+"/results/")

            results_summary = []

            errors = []
            failures = []

            test_cases = {}

            test_results_folder = pa.path+"/test_results/"

            for c_hash, row in pa.csvDict.items():

                report_folder = "%s-%s" % (row['id'], c_hash)

                n_test = 0
                n_skipped = 0
                n_errors = 0
                n_failures = 0

                if os.path.isdir(test_results_folder+report_folder):

                    for report in os.listdir(test_results_folder+report_folder):
                        if re.match(r'TEST-.*\.xml', report):
                            try:
                                # Get test suite info
                                xml = JUnitXml.fromfile(test_results_folder+report_folder+"/"+report)
                                n_test += xml.tests
                                n_skipped += xml.skipped
                                n_errors += xml.errors
                                n_failures += xml.failures
                                # Get errors
                                for tc in xml:
                                    test_id = tc.classname + "#" + tc.name
                                    if test_id not in test_cases:
                                        test_cases[test_id] = {
                                            'commits': 0,
                                            'success': 0,
                                            'failures': 0,
                                            'errors':  0,
                                            'skipped':  0
                                        }

                                    test_cases[test_id]["commits"] += 1

                                    success_tc = True

                                    # Elems in TC contains Failure/Error/Skiped nodes    
                                    for elem in tc:
                                        success_tc = False
                                        # Count failures and errors
                                        if elem.__class__ is Failure:
                                            failures.append(elem.type)
                                            test_cases[test_id]["failures"] += 1
                                        if elem.__class__ is Error:
                                            errors.append(elem.message)
                                            test_cases[test_id]["errors"]+= 1
                                        if elem.__class__ is Skipped:
                                            test_cases[test_id]["skipped"] += 1
                                    
                                    if success_tc: test_cases[test_id]["success"] += 1

                            except Exception as e:
                                pass

                results_summary.append([
                    int(row['id']),
                    c_hash,
                    n_test,
                    n_test - n_failures - n_errors,
                    n_failures,
                    n_errors,
                    n_skipped
                ])

            self.summary = pd.DataFrame(results_summary, columns = [
                'id',
                'commit',
                'n_test',
                'n_success',
                'n_failures',
                'n_errors',
                'n_skipped'
            ]).sort_values(by=['id'])

            error_df = None
            failures_df = None
            test_case_df = None

            if len(errors) > 0:
                self.error_df = pd.DataFrame.from_records(self.countWords(errors), columns=['error', 'count'])
                # Data is cached
                self.error_df.to_csv(errors_count_path, index=False)
            if len(failures) > 0:
                self.failures_df = pd.DataFrame.from_records(self.countWords(failures), columns=['exception', 'count'])
                # Data is cached
                self.failures_df.to_csv(failures_count_path, index=False)
            if len(test_cases) > 0:
                self.test_case_df = pd.DataFrame.from_dict(test_cases).transpose()
                self.test_case_df.reset_index(level=0, inplace=True)#['test_name'] = test_case_df.index
                self.test_case_df.rename(columns={"index":"test_name"}, inplace=True)
                # Data is cached
                self.test_case_df.to_csv(test_cases_rank_path, index=False)

            # Data is cached
            self.summary.to_csv(summary_path, index=False)


if __name__ == "__main__":
    
    pa = ProjectTestAnalysis(sys.argv[1], 2, root="/home/jovyan/work", forceGenerate=True)

    summary = pa.getSummary()

    
    