docker run -d --rm\
    -v $PWD/results:/home/bugs/results \
    -v $PWD/py:/home/bugs/py \
    -v $PWD/projects:/home/bugs/projects \
    -v $PWD/configFiles:/home/bugs/configFiles \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -w /home/bugs/ \
    --name build-experiment-$2 \
    --privileged=true maes95/build-analyzer:0.3.3-dev python py/checkBuildHistory.py $1