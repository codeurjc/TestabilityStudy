# Pull base image.
FROM python:3.9

# Install Docker

RUN curl -fsSL https://get.docker.com | sh

RUN pip install --upgrade pip
ADD py/requirements.txt requirements.txt
RUN pip install -r requirements.txt

VOLUME ["/home/bugs/projects/"]

RUN echo "PS1='\[\033[1;36m\]BuildAnalycer-0.3.3-dev \[\033[1;34m\]\w\[\033[0;35m\] \[\033[1;36m\]# \[\033[0m\]'" >> ~root/.bashrc

WORKDIR /home/bugs/

CMD ["bash"]
# BUILD docker build -f dockerfiles/build-analyzer.Dockerfile -t  maes95/build-analyzer:0.3.3-dev .