import logging
import json
import yaml

from pymongo import MongoClient
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener

# setup logging
logging.basicConfig(
    filename='progress.log',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s'
)

# read config file
config = {}
with open("config/config.yaml", 'r') as stream:
    try:
        logging.info('reading file')
        config = yaml.load(stream)
        logging.info('done reading file')
    except yaml.YAMLError as exc:
        logging.error(exc)

config_keys = config["keys"]
# Variables that contains the user credentials to access Twitter API
access_token = config_keys["TWITTER_ACCESS_TOKEN"]
access_token_secret = config_keys["TWITTER_TOKEN_SECRET"]
consumer_key = config_keys["TWITTER_CONSUMER_KEY"]
consumer_secret = config_keys["TWITTER_CONSUMER_SECRET"]

# create mongodb client connection
connection_string = "mongodb://{}:{}@{}:{}".format(
    config["users"]["MONGO_DB_TWITTER_USER"],
    config["passwords"]["MONGO_DB_TWITTER_PASSWORD"],
    config["vms"]["DIGITAL_OCEAN_IP"],
    config["vms"]["DIGITAL_OCEAN_MONGO_PORT"]
)
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
                    "hashtag": hashtag["text"],
                    "created_at": tweet["created_at"],
                    "followers_count": tweet["user"]["followers_count"]
                }

    def insert_data(self, tweet):
        json_tweet = json.loads(tweet)
        if 'entities' in tweet:
            for hashtag in self.extract_data(json_tweet):
                hashtag_exchange_collection.insert(hashtag)
                if self.processed_count % 100 == 0:
                    logging.info(
                        (
                            "tweets processed since startup:{}, "
                            "last hashtag:{}"
                        ).format(self.processed_count, hashtag)
                    )
                self.processed_count += 1

        elif 'warning' in tweet:
            logging.warning(tweet)

        return True

    def on_disconnect(self, notice):
        logging.error(notice)


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
