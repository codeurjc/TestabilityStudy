import subprocess
import re
import os
import sys
import docker

DELIMITER="|=|"
DEFAULT_TIMEOUT=300

# PROCESS

class ExecutorManager():

    def execute(self, command, output): raise NotImplementedError

class ProcessManager(ExecutorManager):

    def __init__(self, output, log_name="PROCESS MANAGER"):
        self.outfile = output
        self.log_name = log_name

    @staticmethod
    def default_exec(command, output=None, returnOutput=False):
        dpm = ProcessManager(open("default.log", 'w'), "DEFAULT PROCESS MANAGER")
        exit_code, text = dpm.execute(command, output, returnOutput)
        dpm.close()

    def execute(self, command, output=None, returnOutput=False):
        
        if returnOutput:
            with open('/tmp/run', 'w+') as out:
                exit_code, _ = self.execute(command, output=out)
            with open('/tmp/run', 'r+', errors='ignore') as out:
                text = out.read()
            self.execute("rm /tmp/run")
            return exit_code, text
        else:
            if output is None:
                output=self.outfile
            exit_code = subprocess.call(command, shell=True, stdout=output, stderr=output)
            return exit_code, None

    def log(self, message, output=None):
        if output is None:
            output=self.outfile
        subprocess.call("echo [ %s ] %s"%(self.log_name, message), shell=True, stdout=output, stderr=output)

    def close(self):
        if self.outfile is not None:
            self.outfile.close()

# GIT

class GitManager:

    def __init__(self, executor_manager, base_commit):
        self.executor_manager = executor_manager
        self.base_commit = base_commit
        #self.executor_manager.execute("git checkout -f %s" % base_commit)

    def change_commit(self,commit_hash):
        with open(os.devnull) as out:
            self.executor_manager.execute("git clean -fdx", out)
        self.executor_manager.execute("git checkout -f %s" % commit_hash)

    def getAllCommits(self):
        _, out = self.executor_manager.execute('git log %s --pretty=format:"%%h%s%%ad%s%%s" --date=iso8601 --reverse'%(self.base_commit, DELIMITER, DELIMITER), returnOutput=True)
        return out.strip().split('\n')

# DOCKER

class DockerManager():

    def __init__(self, process_manager):
        self.client = docker.from_env()
        self.containers = []
        self.pm = process_manager
    
    def container_exist(self, container_id):
        try:
            self.client.containers.get(container_id)
            return True
        except docker.errors.NotFound as e:
            return False

    def execute(self, docker_image, project, command, output, timeout=DEFAULT_TIMEOUT):
        """Executes 'command' in a Docker container created by 'docker_image'.
            If container does not exist, then create one and executes 'command'
            
            Keyword arguments:
            
                docker_image -- An existing Docker image. If not is available locally, it will be downladed
                
                project      -- Project folder name which container uses as work-directory
                
                command      -- Bash command which will be execute in the container
                
                output       -- File path to store docker logs
        """

        container_id = "aux-container-%s-%s"% (re.sub('[:/]', '_', docker_image),project)
        
        if not self.container_exist(container_id):
            # NOT EXISTS -> CREATE
            workdir = "/home/bugs/projects/%s" % project

            container = self.client.containers.run(docker_image,"tail -f /dev/null",
                name=container_id, 
                detach=True,
                volumes_from=[os.environ['HOSTNAME']],
                working_dir=workdir,
                auto_remove=True
            )
            self.containers.append(container)
        else:
            container = self.client.containers.get(container_id)
        
        with open(output, "wb+") as out:
            (exit_code, container_output) = container.exec_run("timeout %d bash -c '%s'"%(timeout,command))
            out.write(container_output)
            return exit_code

    def shutdownContainers(self):
        for container in self.containers:
            container.stop()
        self.client.close()

if __name__ == "__main__":
    pm = ProcessManager(open("default.log", 'w'), "DEFAULT PROCESS MANAGER")
    dm = DockerManager(pm)
    code = dm.execute("java-maven-ant:0.1", "assertj-core", "unset MAVEN_CONFIG && ./mvnw clean compile -X", "build.log")
    dm.shutdownContainers()
    print(code)
    