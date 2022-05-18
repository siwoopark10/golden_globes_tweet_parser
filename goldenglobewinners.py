import os
import re
import json
import nltk
import spacy
model = spacy.load('en_core_web_sm')
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.tokenize import TreebankWordTokenizer
wordTokenizer = TreebankWordTokenizer()
from nltk.corpus import stopwords
stop = stopwords.words('english')
def read_tweets():
    cwd = os.getcwd()
    path = cwd + '/gg2013.json'
    f = open(path)

    tweet_json = json.load(f)
    tweets = []
    for tweet in tweet_json:
        tweets.append(tweet["text"].lower())
    return tweets

tweets = read_tweets()

filterRegExPatterns = ['host?[s]', 'hosting', 'hosted', 'won best', 'winner', 'wins', 'presented', 'presenting', 'red carpet', 'best dressed', 'best dress', 
'worst dressed', 'worst dress'] 
filterRegExPatternJoin = "|".join(filterRegExPatterns)
filterRegEx = re.compile(filterRegExPatternJoin, re.IGNORECASE)
#re ex for removing all the rt
filterRetweetRegEx = re.compile('^RT', re.IGNORECASE)
filteredTweets = []
count = 0
for tweet in tweets:
    if(filterRegEx.search(tweet) and not filterRetweetRegEx.search(tweet)):
        count += 1
        tweetCleaned = re.sub(r'[^a-zA-Z0-9 ]',r'',tweet)
        filteredTweets.append(tweetCleaned)
blacklist = ['golden', 'globes', 'goldenglobes', '#goldenglobes', '#golden']
stop.append(blacklist)
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

def identify_entities(text, stop_words):
    tags = {}
    for ent in model(text).ents:
        entity = ent.text.strip()
        if entity not in tags and len(entity) > 1:
            # remove stopwords
            entity_split = [w for w in entity.split() if w.lower() not in stop_words]
            if len(entity_split) != 0:
                entity = ' '.join(entity_split)
                # if entity is a single word that is 'the' or is a single character
                if (len(entity.split()) == 1) or len(entity) == 1:
                    pass
                else:
                    tags[entity]=[ent.label_]
    return tags
#find hosts
def findHosts(tweets):
    entity_freq_dict = {}

    for line in tweets:
        match = re.search(hostre, line)
        if match:
            for entity in identify_entities(line, stop).keys():
                if entity not in entity_freq_dict:
                    entity_freq_dict[entity] = 1
                else:
                    entity_freq_dict[entity] += 1
    return entity_freq_dict
    #for tweet in tweets:
     #       filterText = ' '.join(word for word in tweet.split() if word.lower() not in stop and word.lower() not in blacklist)
      #      unigram = wordTokenizer.tokenize(filterText)
       #     posTag = nltk.pos_tag(unigram)
        #    
         #   for(data, tag) in posTag:

                    #Check for proper nouns
          #      if tag == 'NNP':
                     
           #         addToDict(data, hostName)
                #if both the words in bigram are proper nouns, mark the bigram as probable host name        

                    
                        #numNames += 1
                
            #if numNames == 2:
                   
                 #   name = "%s %s" % bigram
                    
                 #   addToDict(name, hostName)
hostName  = findHosts(filteredTweets)
temp = 0
for key in hostName:
    if hostName[key] > temp:
        temp = hostName[key]
for key in hostName:
    if temp == hostName[key]:
        hosts.append(key) 
print(hostName)
print(hosts)