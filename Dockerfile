FROM ubuntu:20.04
MAINTAINER wangrongxiang

WORKDIR /root/dev/source-code/seahub_loginer
COPY . ./

RUN apt-get -y update && \
    apt-get install -y sudo && \
    sudo apt-get install -y python3-pip python3 python3-dev && \
    sudo python3 -m pip install --upgrade pip && \
    pip install virtualenv && \
    virtualenv env

ENV VIRTUAL_ENV env                     # activating environment
ENV PATH env/bin:$PATH                  # activating environment

RUN pip install -r requirements.txt

EXPOSE 5000

#ENTRYPOINT ["python3", "app.py", "-m"]
ENTRYPOINT ["uwsgi", "config.ini"]