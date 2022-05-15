import os
import re
import json
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk import pos_tag


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

#dictionary for hosts
hostName = dict()
def addToDict(key,dictionary):
    if key in dictionary:
        dictionary[key] += 1
    else:
        dictionary[key] = 1

#final list output of hosts
hosts = []
#regex pattern for hosts
hostRegEx = ['host','hosts','hosted','hosting']
hostJointRegEx = '|'.join(hostRegEx)
hostre = re.compile(hostJointRegEx, re.IGNORECASE)

#find hosts
def findHosts(tweets):
    for tweet in tweets:
        if hostre.search(tweet):
            unigram = word_tokenize(tweet)
            bigrams = nltk.bigrams(unigram)
            for bigram in bigrams:
                numNames = 0
                POStag = nltk.pos_tag(bigram)
                for (text, tag) in POStag:
                    if tag == 'NNP': #tag for proper noun
                        numNames += 1
                if numNames ==2:
                    name = "%s %s" % bigram
                    addToDict(name, hostName)
temp = 0
for key in hostName:
    if hostName[key] > temp:
        temp = hostName[key]
for key in hostName:
    if temp < 1.05 * hostName[key]:
        hosts.append(key) 
print(hosts)