FROM maven:3-jdk-8-slim

#####
# Ant
#####

# Preparation

ENV ANT_VERSION 1.10.7
ENV ANT_HOME /etc/ant-${ANT_VERSION}

# Installation

RUN cd /tmp\
    && curl -fsSL -o /tmp/apache-ant-${ANT_VERSION}-bin.tar.gz http://ftp.cixug.es/apache/ant/binaries/apache-ant-${ANT_VERSION}-bin.tar.gz\
    && mkdir ant-1.10.7\
    && tar -zxvf apache-ant-${ANT_VERSION}-bin.tar.gz --directory ant-${ANT_VERSION} --strip-components=1\
    && mv ant-${ANT_VERSION} ${ANT_HOME}
ENV PATH ${PATH}:${ANT_HOME}/bin

# Cleanup

RUN rm /tmp/apache-ant-${ANT_VERSION}-bin.tar.gz
RUN unset ANT_VERSION

# BUILD docker build -f dockerfiles/java-maven-ant.Dockerfile -t java-maven-ant:0.1 .