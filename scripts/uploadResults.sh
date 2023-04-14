for dataset in "Apache" "Github" "Many4J" "All"
do
    echo $dataset
    rclone copy notebooks/ProjectAnalysis/TestAnalysis/TestResults-$dataset.xlsx OneDrive:/Research/BugsBirth/Testeability/results/
done