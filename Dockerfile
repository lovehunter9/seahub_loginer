FROM ubuntu:20.04
MAINTAINER wangrongxiang

WORKDIR /root/dev/source-code/seahub_loginer
COPY . ./

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3", "app.py", "-m"]