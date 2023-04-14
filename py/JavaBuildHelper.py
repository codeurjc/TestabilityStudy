import json
import os
import re
from utils import GitManager, DockerManager

NO_BUILD_MESSAGE="BuildAnalycer: No build system detected"

#DOCKER_IMAGE = "java-maven-ant:0.1"
DOCKER_IMAGE = "maven:3-jdk-8-slim"

BUILD_SYSTEMS=[
    { "build_system": "Maven", "build_file": "pom.xml", "build_command": lambda build_file : "mvn clean compile -X"},
    # { "build_system": "Gradle", "build_file": "gradlew", "build_command": lambda build_file : "%s build -x test"%build_file},
    # { "build_system": "Ant", "build_file": "build.xml", "build_command": lambda build_file : "ant compile -v -f %s"%build_file}
]

class JavaBuildHelper():

    def __init__(self, pm):
        self.pm = pm

    def getBuildConfigs(self, previous_build=None):

        """
            Return a list of build config like this: 
            {
                "build_system": " Maven | Ant | Gradle ",
                "docker_image": " $DOCKER_IMAGE ",
                "build_command": "<bash_script>",
                "build_file": "<build_file_path>"
                "works": false
            }
        """

        build_configs = []

        # GETTING BUILD SYSTEMS

        self.pm.log("Getting build system")
        
        for bs in BUILD_SYSTEMS:

            exist, buildfile = self.searchBuildFile(bs["build_file"])
            if exist:
                build_config = {
                    "build_system": bs["build_system"],
                    "docker_image": DOCKER_IMAGE,
                    "build_command": bs["build_command"](buildfile),
                    "build_file": buildfile,
                    "works": False
                }
                build_configs = build_configs + [build_config]
                
        if len(build_configs) == 0:
            # NO BUILD SYSTEM DETECTED
            build_config = {
                "build_system": "NOT_FOUND",
                "docker_image": "-",
                "build_command": "echo '%s' && exit 1"%NO_BUILD_MESSAGE,
                "build_file": "-",
                "works": False
            }
            return [build_config]
        else:
            return build_configs
    
    def searchBuildFile(self, file_name):
        depth=1
        _, result = self.pm.execute('find . -maxdepth %d -name "%s"'%(depth, file_name), returnOutput=True)
        if result != "":
            result = result.split('\n')
            result.remove("")
            result.sort(key=len)
            buildfile = result[0]
            return True, buildfile
        else:
            return False, ""

    def executeBuildSystem(self, project, docker_manager, build_config, log_file):

        if build_config['build_system'] == "NOT_FOUND":
            # Write failed log
            with open(log_file, "w+") as out: out.write(NO_BUILD_MESSAGE)
            return -1
        else:
            # Execute build
            exit_code = docker_manager.execute(build_config["docker_image"], project, build_config["build_command"], log_file)
            return exit_code