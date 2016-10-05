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
        result = q.enqueue(process_tweet, data)
        return True
        
    def on_error(self, status):
        print status
        
if __name__ == '__main__':
    
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    
    stream.filter(track=['Trump', 'Clinton'])
