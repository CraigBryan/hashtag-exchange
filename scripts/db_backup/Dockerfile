FROM python:3

RUN mkdir -p /scripts/log

RUN apt-get update
RUN apt-get install -y mongodb

COPY ./requirements.txt requirements.txt
COPY ./backup_database.py backup_database.py
RUN pip install -r ./requirements.txt
