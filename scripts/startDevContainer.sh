docker run -it --rm\
    -v $PWD/results:/home/bugs/results \
    -v $PWD/py:/home/bugs/py \
    -v $PWD/projects:/home/bugs/projects \
    -v $PWD/configFiles:/home/bugs/configFiles \
    -v $PWD/tmp:/home/bugs/tmp \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --privileged=true maes95/build-analyzer:0.3.2-dev