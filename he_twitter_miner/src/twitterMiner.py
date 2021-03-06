import logging
import json
import yaml
import time
import sys
from pymongo import MongoClient
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import dateutil.parser





class DataInserter():
    processed_count = 0

    def __init__(self, hashtag_exchange_collection):
        self.hashtag_exchange_collection = hashtag_exchange_collection
    
    def extract_data(self, tweet):
        hashtags = tweet['entities']['hashtags']
        if hashtags:
            for hashtag in hashtags:               
                createdDate = dateutil.parser.parse(tweet["created_at"])
                yield {
                    "hashtag": hashtag["text"],
                    "created_at": createdDate,
                    "followers_count": tweet["user"]["followers_count"]
                }

    def insert_data(self, json_tweet):

        if 'entities' in json_tweet:
            for hashtag in self.extract_data(json_tweet):
                self.hashtag_exchange_collection.insert(hashtag)
                if self.processed_count % 100 == 0:
                    logging.info(
                        (
                            "tweets processed since startup:{}, "
                            "last hashtag:{}"
                        ).format(self.processed_count, hashtag)
                    )
                self.processed_count += 1
        return True


class StdOutListener(StreamListener):

    def __init__(self, hashtag_exchange_collection):
        self.data_inserter = DataInserter(hashtag_exchange_collection)
        super(StdOutListener, self).__init__()
      
    def on_data(self, raw_data):
        data = json.loads(raw_data)
        if 'in_reply_to_status_id' in data:
            return self.data_inserter.insert_data(data)
        return super(StdOutListener, self).on_data(raw_data)
  
    def keep_alive(self):
        logging.info("kept alive message received")

    def on_exception(self, exception):
        logging.error("exception received notice: {}".format(exception))
        return False

    def on_error(self, status_code):
        logging.error("exception received notice: {}".format(status_code))
        return False


    def on_disconnect(self, notice):
        logging.warning("disconnect received notice: {}".format(notice))
        return False

    def on_warning(self, notice):
        logging.warning("Warming received notice: {}".format(notice))
        
class TwitterMiner():
    
    def __init__(self):
        self.configure_logging()
        self.load_config()
        logging.info('connecting to database')
        self.client = MongoClient(self.connection_string)
        self.hashtag_exchange_collection = self.client.hashtagExchange[
            'rawTwitterHashtags'
            ]
        logging.info('connection established')
        listener = StdOutListener(self.hashtag_exchange_collection)
        auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.stream = Stream(auth, listener)

    def load_config(self):
        self.config = {}
        with open("config/config.yaml", 'r') as config_stream:
            try:
                logging.info('reading file')
                self.config = yaml.load(config_stream)
                logging.info('done reading file')
            except yaml.YAMLError as exc:
                logging.error(exc)

        config_keys = self.config["keys"]
        # Variables that contains the user credentials to access Twitter API
        self.access_token = config_keys["TWITTER_ACCESS_TOKEN"]
        self.access_token_secret = config_keys["TWITTER_TOKEN_SECRET"]
        self.consumer_key = config_keys["TWITTER_CONSUMER_KEY"]
        self.consumer_secret = config_keys["TWITTER_CONSUMER_SECRET"]
        # create mongodb client connection
        self.connection_string = "mongodb://{}:{}@{}:{}".format(
            self.config["users"]["MONGO_DB_TWITTER_USER"],
            self.config["passwords"]["MONGO_DB_TWITTER_PASSWORD"],
            self.config["vms"]["DIGITAL_OCEAN_IP"],
            self.config["vms"]["DIGITAL_OCEAN_MONGO_PORT"]
            )
        logging.info("CONNECTION STRING:{}".format(self.connection_string))

    def configure_logging(self):
        # setup logging
        logging.basicConfig(
            filename='progress.log',
            level=logging.DEBUG,
            format='%(asctime)s %(message)s'
            )
            
    def start_mining(self):
        self.stream.sample(stall_warnings=True, languages=['en'])
            