from twitterMiner import TwitterMiner
import logging
import time

if __name__ == '__main__':
    attempts = 0   
    while attempts < 5:     
        try:
            twitter_miner = TwitterMiner()
            twitter_miner.start_mining()
        except Exception as e:
            logging.error(
                "exception received attempting to start again after timeout:{}"
                .format(e))
        time.sleep((attempts)*30+30)
        attempts += 1
    logging.info("too many restart attempts, shutting down")
        
    