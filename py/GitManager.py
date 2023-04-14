import git

DELIMITER="|=|"

class GitManager:

    def __init__(self, project_path, base_commit):
        self.project_path = project_path
        self.base_commit = base_commit
        self.repo = git.Repo(project_path)

    def change_commit(self,commit_hash):
        self.repo.git.clean("-fdx")
        self.repo.git.checkout('-f',commit_hash) 

    def getAllCommits(self):
        res = self.repo.git.log(self.base_commit,'--pretty=format:"%%H%s%%ad%s%%s"'%(DELIMITER, DELIMITER),'--date=iso8601','--reverse')
        return res.strip().split('\n')

if __name__ == "__main__":
    gm = GitManager("~/work/projects/maven","12f3e7e878e3a22a696f7ba9b5c615d520807afb")
    print(gm.getAllCommits())