import os
import re
import json
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize


def read_tweets():
    cwd = os.getcwd()
    path = cwd + '\\gg2013.json\\gg2013.json'
    f = open(path)

    tweet_json = json.load(f)
    tweets = []
    for tweet in tweet_json:
        tweets.append(tweet["text"].lower())
    return tweets

tweets = read_tweets()

for tweet in tweets:
    words = word_tokenize(tweet)
    if 'won' in words:
        index = words.index('won')
        # print(words[index:])