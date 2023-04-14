import unittest
from checkBuildHistory import BuildChecker
from javaBuildHelper import NO_BUILD_MESSAGE
from utils import ProcessManager
from time import gmtime, strftime, sleep
import os
import re
from parameterized import parameterized

def getLog(path):
    with open(path,"r") as f:
        return f.read()

def get_timestamp():
    now = datetime.now()
    return now.strftime("%H.%M.%S")

test = [  
        # ('NoBuildSystemTest',                    'Closure-test-1-config.json',         '7e0d71b3', 'FAIL',     NO_BUILD_MESSAGE),
        # ('SuccessBuildTest-Closure',             'Closure-test-2-config.json',         '49e9565f', 'SUCCESS',  'BUILD SUCCESS'),
        # ('FailedBuildTest',                      'Closure-test-3-config.json',         '86e26932', 'FAIL',     'BUILD FAILED'),
        ('SuccessBuildTest-myfaces-html5',       'myfaces-html5-test-1-config.json',   'a41da370', 'SUCCESS',  'BUILD SUCCESS'),
        ('SuccessBuildTest-myfaces-html5-2',     'myfaces-html5-test-2-config.json',   'a41da370', 'SUCCESS',  'BUILD SUCCESS'),
        ('SuccessBuildTest-MavenWrapper',        'AssertJCore-test-1-config.json',     'fc37b2d6', 'SUCCESS',  'BUILD SUCCESS')
        # ('SuccessBuildTest_DeepConfigFile',     'Time-test-1-config.json',      '0f951f39', 'SUCCESS',  'BUILD SUCCESS'),
        # ('Case 1',                              'Math-test-1-config.json',      '0da657a6', 'SUCCESS',  'BUILD SUCCESS'), 
        # ('Case 2',                              'Lang-test-1-config.json',      '687b2e62', 'SUCCESS',  'BUILD SUCCESS'),
        # ('Case 2.1',                            'Lang-test-2-config.json',      '5ac897ad', 'SUCCESS',  'BUILD SUCCESS')
    ]

class CheckBuildTest(unittest.TestCase):

    @parameterized.expand(test)
    def test_simple(self,name,config, commit, state, pattern):
        self.bcheck = BuildChecker("configFiles/test/%s"%config, test=True)
        self.delete_path = self.bcheck.path
        self.root = self.bcheck.root
        self.test_name = name
        self.bcheck.checkBuild()
        self.bcheck.finish("FINISHED EXPERIMENT SUCCESSFULLY - TEST MODE")
        commits = self.bcheck.csvDict
        
        # CHECK BUILD STATUS 
        self.assertEqual(commits[commit]['build'], state)

        dir_ = 'results/%s/experiment_0/logs/'%self.bcheck.config['project']

        logs = [f for f in os.listdir(dir_) if re.match(r'0-%s-attempt-\d.log'%commit, f)]

        # CHECK LOG 
        self.assertRegex(getLog(dir_+logs[-1]), pattern)
    
    # def test_multi(self):
    #     config = "Lang-test-4-config.json"
    #     self.bcheck = BuildChecker("configFiles/_test/%s"%config, test=True)
    #     self.delete_path = self.bcheck.path
    #     self.bcheck.checkBuild()
    #     self.bcheck.finish("FINISHED EXPERIMENT SUCCESSFULLY - TEST MODE")
    #     commits = self.bcheck.csvDict
        
    #     # CHECK BUILD STATUS 
    #     self.assertEqual(commits['c745cdf5']['build'], "SUCCESS")
    #     self.assertEqual(commits['1161a577']['build'], "SUCCESS")
    #     self.assertEqual(commits['123836ed']['build'], "SUCCESS")
    #     self.assertEqual(commits['0bf26e0d']['build'], "SUCCESS")

    #     dir_ = 'analysis/%s/experiment_0/logs/'%self.bcheck.config['project']

    #     # CHECK LOGS

    #     self.assertRegex(getLog(dir_+"0-c745cdf5-attempt-1.log"), 'BUILD SUCCESS')
    #     self.assertRegex(getLog(dir_+"1-1161a577-attempt-1.log"), 'BUILD SUCCESS')
    #     self.assertRegex(getLog(dir_+"2-123836ed-attempt-1.log"), 'BUILD FAILURE')
    #     self.assertRegex(getLog(dir_+"2-123836ed-attempt-2.log"), 'BUILD SUCCESS')
    #     self.assertRegex(getLog(dir_+"3-0bf26e0d-attempt-1.log"), 'BUILD FAILURE')
    #     self.assertRegex(getLog(dir_+"3-0bf26e0d-attempt-2.log"), 'BUILD SUCCESS')

    def tearDown(self):
        tmp_folder="%s/tmp/test/%s_%s"%(self.root, self.test_name, strftime("%d%b%Y_%X", gmtime()))
        ProcessManager.default_exec("cp -r %s %s"%(self.delete_path, tmp_folder))
        ProcessManager.default_exec("rm -rf %s/results/%s"%(self.root, self.bcheck.config['project']))
        
if __name__ == '__main__':
    if not os.path.exists("tmp/test/"): os.mkdir("tmp/test/")
    ProcessManager.default_exec("rm -rf tmp/test/**")
    unittest.main(verbosity=2)
        

