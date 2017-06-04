FROM python:3

WORKDIR /usr/git

RUN git clone https://github.com/tweepy/tweepy.git 
WORKDIR /usr/git/tweepy
RUN python setup.py install

WORKDIR /usr/src/app
RUN pip install pymongo
RUN pip install pyyaml
COPY . .
CMD [ "python", "./serverStartup.py" ]