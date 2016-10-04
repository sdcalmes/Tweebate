import os
import re
from redis import Redis
import json
import pymongo
from pymongo import MongoClient
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment

client = MongoClient('localhost', 27017)
db = client.tweet_data

def process_tweet(tweet):
    tweet = json.loads(tweet)
    tweet_text = tweet.get('text')
    #process the actual text here. remove hashtags, etc.
    trump = word_in_text('trump', tweet_text)
    clinton = word_in_text('clinton', tweet_text)
    if trump is False and clinton is False:
        return 0
    vs = vaderSentiment(tweet_text.encode('utf-8'))
    if vs.get('neu') == 1 or (vs.get('compound') > -.35 and vs.get('compound') < .35):
        return 0
    #get sentiment
    if vs.get('compound') > .35:
        pos = True
    if vs.get('compound') < -.35:
        pos = False
    post = {
        'trump' : trump,
        'clinton' : clinton,
        'vader' : vs,
        'positive' : pos,
        'text' : tweet_text
    }
    
    posts = db.tweets
    post_id = posts.insert_one(post).inserted_id
    count_tweets(True, 'trump')
   
def word_in_text(word, text):
    word = word.lower()
    text = text.lower() if text is not None else "GARBAGE"
    match = re.search(word, text)
    if match:
        return True
    return False
    
def count_tweets(pos, person):
    posts = db.tweets
    found = posts.find({"$and": [{'positive' : pos}, {person : True}]})
    print found.count()
    return found.count()