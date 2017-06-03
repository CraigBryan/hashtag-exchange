#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from pymongo import MongoClient
from pprint import pprint
import logging
import json


#setup logging
logging.basicConfig(filename='progress.log',level=logging.DEBUG, format='%(asctime)s %(message)s')

#Variables that contains the user credentials to access Twitter API 
access_token = <KEY HERE>
access_token_secret = <KEY HERE>
consumer_key = <KEY HERE>
consumer_secret = <KEY HERE>

#create mongodb client connection
connection_string = 'mongodb://twitterService:Ej9gZVAvyTwxeqlHaIVG@198.199.65.123:27027'
logging.info('connecting to database')
client = MongoClient(connection_string)
hashtag_exchange_collection = client.hashtagExchange['rawTwitterHashtags']
logging.info('connection established')

class DataInserter():
    processed_count = 0
    
    def extract_data(self, tweet):
        hashtags = tweet['entities']['hashtags']
        if hashtags:
            for hashtag in hashtags:
                
                yield {
                    "hashtag":hashtag["text"],
                    "created_at":tweet["created_at"],
                    "followers_count": tweet["user"]["followers_count"]}
        return False
    def insert_data(self, tweet):
         
        json_tweet = json.loads(tweet)
        if 'entities' in tweet:
            for hashtag in self.extract_data(json_tweet): 
                hashtag_exchange_collection.insert(hashtag)
                if self.processed_count% 100 == 0:
                    logging.info("tweets processed since startup:{}, last hashtag:{}"
                        .format(self.processed_count, hashtag))
                self.processed_count += 1
        elif 'warning' in tweet:
            logging.warning(tweet)
        return True
    def on_disconnect(self, notice):
        log.error(notice)
        return
        

class StdOutListener(StreamListener):
    def __init__(self):
        self.data_inserter = DataInserter()
    def on_data(self, data):
        self.data_inserter.insert_data(data)
        return True

    def on_error(self, status):
        logging.info(status)


if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    stream.sample(stall_warnings=True, languages=['en'])
    