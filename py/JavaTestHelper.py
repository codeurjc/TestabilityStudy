import shutil
import os

class JavaTestHelper():

    def __init__(self, pm):
        self.pm = pm

    def compileTest(self, project, docker_manager, build_config, log_file):

        if build_config["build_system"] == "Maven":
            buildTestCommand = "mvn test-compile"
        if build_config["build_system"] == "Ant":
            buildTestCommand = "ant compile.tests"

        # Execute build
        exit_code = docker_manager.execute(build_config["docker_image"], project, buildTestCommand, log_file)
        return exit_code

    def runAllTest(self, project, docker_manager, build_config, log_file):
        
        if build_config["build_system"] == "Maven":
            testCommand = "mvn test"
        if build_config["build_system"] == "Ant":
            testCommand = "ant test"

        # Execute build
        exit_code = docker_manager.execute(build_config["docker_image"], project, testCommand, log_file, timeout=3600)
        return exit_code

    def saveSurefireReports(self, project, dest_folder_name):
        destFolder = project.test_results_path + dest_folder_name
        for root, directories, files in os.walk("."):
            for directory in directories:
                if "surefire-reports" == directory:
                    print(root, directory)
                    srcFolder = os.path.join(root, directory)
                    shutil.copytree(srcFolder, destFolder, dirs_exist_ok=True)

class Proyect():
    project_folder = "/home/bugs/projects/qpid-proton/"
    test_results_path = "/home/bugs/tmp/"

if __name__ == "__main__":

    project = Proyect()
    dest = "results/"

    jth = JavaTestHelper(None)
    jth.saveSurefireReports(project, dest)
