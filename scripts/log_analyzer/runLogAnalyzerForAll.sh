for result_path in results/*; do
    
    if [ -d $result_path ]
    then
        projectName=$(basename $result_path)
        if [ -d "notebooks/ProjectAnalysis/TestAnalysis/results/${projectName}" ]
        then
            echo $projectName
            ./scripts/log_analyzer/runLogAnalyzer.sh $projectName
        fi
    fi
done