from twitterMiner import TwitterMiner
import logging
import time

if __name__ == '__main__':

    while True:
        try:
            twitter_miner = TwitterMiner()
            twitter_miner.start_mining()
            
        except Exception as e:
            logging.error("exception received {}".format(e))
        logging.info("waiting for 10 seconds before retrying")
        time.sleep(10)