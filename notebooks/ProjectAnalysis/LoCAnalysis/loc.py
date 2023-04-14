from pygount import ProjectSummary, SourceAnalysis
import os
import sys
import pathlib

def calculateLOC(path, lang, extension):
    """Return number of files and lines of code from a project

        Parameters
        ----------
        path : str
            Path to project's folder
        lang : str
            Main language of the project. Only the lines of this language will be considered. ( i.e. 'Java' )
        extension : str
            Language file extension ( i.e '.java' )

        Returns
        -------

        int: Number of files
        int: Number of lines

    """

    source_paths = list(pathlib.Path(path).glob(extension))
    project_summary = ProjectSummary()
    for source_path in source_paths:

        source_analysis = SourceAnalysis.from_file(source_path, "project")
        project_summary.add(source_analysis)

    if lang in project_summary.language_to_language_summary_map:

        lang_summary = project_summary.language_to_language_summary_map[lang]

        return lang_summary.file_count, lang_summary.code_count
    
    else:

        return 0,0
        
if __name__ == "__main__":
    # docker run -d -v $PWD:/home/jovyan/work/ -w /home/jovyan/work/ jupyter-bugs:v2 python notebooks/ProjectAnalysis/LoCAnalysis/loc.py
    print(calculateLOC("projects/%s/"%(sys.argv[1]),"Java","**/*.java"))