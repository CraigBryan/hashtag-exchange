FROM python:3

RUN mkdir -p /scripts/log

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
RUN echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.0.list
RUN apt-get update

RUN apt-get install mongodb-org-tools=3.4.1

COPY ./requirements.txt requirements.txt
COPY ./backup_database.py backup_database.py
RUN pip install -r ./requirements.txt
