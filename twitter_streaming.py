from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import os
import ConfigParser
import sys
from redis import Redis
from rq import Queue
from process import process_tweet

q = Queue('tweets', connection = Redis())
config = ConfigParser.RawConfigParser()
config.read('config.ini')

access_token = config.get('TokenInfo', 'access.token')
access_token_secret = config.get('TokenInfo', 'access.token.secret')
consumer_key = config.get('TokenInfo', 'consumer.key')
consumer_secret = config.get('TokenInfo', 'consumer.secret')

class StdOutListener(StreamListener):
    
    def on_data(self, data):
        #print data
        result = q.enqueue(process_tweet, data)
        #statinfo = os.stat('out.txt')
        #if statinfo.st_size > 50*1024:
        #    exit(1)
        return True
        
    def on_error(self, status):
        print status
        
if __name__ == '__main__':
    
    #Handle twitter authentication and connection to streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    
    #filter tweets. Do more filtering during analysis
    stream.filter(track=['Trump', 'Clinton'])
