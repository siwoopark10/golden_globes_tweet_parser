from ast import keyword
from nis import cat
import os
import re
import json
import nltk
from nltk.util import ngrams
import spacy
model = spacy.load('en_core_web_sm')
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.tokenize import TreebankWordTokenizer
wordTokenizer = TreebankWordTokenizer()
from nltk.corpus import stopwords
stop = stopwords.words('english')
import imdb
import gender_guesser.detector as gender
# create an instance of the IMDb class
ia =imdb.Cinemagoer()
 
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
#host name stored in hosts. if there is only one host, their name will be at hosts[0]

def findAwards():
    counter= {}
    awards = []
    endwords = ['picture','drama','film','musical','television']
    trash  = []
    for x in filteredTweets:
        tweet = x.split()
        for endword in endwords:
            if endword in tweet and 'best' in tweet:
                s = tweet.index('best')
                e = tweet.index(endword)
                if s < e:
                    award = " ".join(tweet[s:e+1])
                    if award in counter:
                        counter[award] += 1
                    else:
                        counter[award] = 1
    for key in counter:
        if counter.get(key) > 6:
            award = key
            if len(award.split())>3:
                awards.append(award)
    for i in range(0,len(awards)-1):
        for j in range(i+1, len(awards)):
            a1 = awards[i]
            a2 = awards[j]
            if (len(a1)>len(a2) and a2 in a1):
                trash.append(a2)
            if (len(a2)>len(a1) and a1 in a2):
                trash.append(a1)
    for x in trash:
        if x in awards:
            awards.remove(x)

    return awards[0:24]

#stored 25 awards outputed by the parser
awards = findAwards()

def findNomineesPerson(award, data, pattern, keywords, targetpattern,
                                            min_matched,
                                            nominees,
                                            stop_words,recurse):
    if min_matched < 0:
        return nominees

    if recurse:
        if 'tv' in keywords and 'television' not in keywords:
            keywords.append('television')
            # add alternative word for 'Motion Picture'
        if 'Motion Picture' in award and 'motion' not in keywords and 'movie' not in keywords and 'picture' not in keywords:
            keywords.append('movie')
            keywords.append('motion')
            keywords.append('picture')

    gender_detector = gender.Detector()
    if len(nominees) <= 10:
        for line in data:
            match = re.findall(pattern, line.lower())
            match_target_word = re.findall(targetpattern, line.lower()) if targetpattern is not None else [
                '']
            num_matched = len(set(keywords).intersection(set(line.split())))

            if num_matched >= min_matched and (match_target_word or recurse) and match:
                weight = 5 if any('nominee' or 'nominate' or 'lost' or 'lose' in tup for tup in match) else 1
                weight *= num_matched

                tags = identify_entities(line, stop_words)

                for entity in tags.keys():
                    entity_temp = entity
                    entity = entity.strip()
                    entity_split = [w for w in entity.split() if w.lower() not in stop_words]
                    if len(entity_split) != 0:
                        entity = ' '.join(entity_split)
                    if len(entity) > 3:
                        # add more weights for appropriate entity classification
                        if tags[entity_temp] == ['PERSON']:
                            if 'actress' in keywords and gender_detector.get_gender(
                                    entity.split()[0]) == 'female':
                                weight += 10
                            elif 'actor' in keywords and gender_detector.get_gender(entity.split()[0]) == 'male':
                                weight += 10
                            weight += 5
                        else:
                            weight -= 10

                        
                        words_token = word_tokenize(sentence[:index_won])
                        words = []
                        for w in words_token:
                            if not w in stop:
                                words.append(w)

                        bigrams = ngrams(words,2)
                        for bg in bigrams:
                            temp = ' '.join(bg)
                            ret = ia.search_person(temp)
                            name  =  ret[0]['name'].lower()
                            if name in line:
                                if name in nominees:
                                    nominees[name] += weight
                                else:
                                    nominees[name] = weight

                        if entity not in nominees:
                            nominees[entity] = weight
                        else:
                            nominees[entity] += weight
    if len(nominees) <= 10:
        nominee_dict = findNomineesPerson(award, data, pattern, keywords, targetpattern,
                                            min_matched - 1, nominees, stop_words, True)
    return nominee_dict

def findNomineesOther():
    return 0

def findNominees(award):
    tv_sub = r'\btelevision\b'
    line = re.sub(tv_sub, 'tv', award.lower())
    # remove words "best", "performance", "language", "role", in", "a", "an", "any", "made", "for", "by", "b.", "award", and all punctuations
    keypattern = r'\bbest\b|\bperformance\b|\blanguage\b|\brole\b|\bin\b|\ba\b|\ban\b|\bany\b|\bmade\b|\bfor\b|\bby\b|\bb\b|\baward\b|[^\w\s]'
    keywords = re.sub(keypattern, ' ', line.lower()).split()
    if len(keywords) == 1:
        min_matched = 1
    else:
        min_matched = round(len(keywords)*0.6)
    nominees = {}
    nomineeRegEx = ['win','won','nominate','nominated','nominee','lost','lose','nominated']
    nomineeJointRegEx = '|'.join(nomineeRegEx)
    pattern = re.compile(nomineeJointRegEx, re.IGNORECASE)
    category = ''
    if len({'actor','actress','director'}.intersection(set(award.split())))>0:
        category = 'name'
    elif len({'show', 'tv', 'television', 'series'}.intersection(set(award.split()))) > 0:
        category = 'tv'
    elif len({'motion', 'picture', 'film', 'movie'}.intersection(set(award.split()))) > 0:
        category = 'film'
    else:
        category = 'song'
    target_ = ['actor', 'actress', 'director', 'score', 'song','tv']
    for word in target_:
        if word in keywords:
            targetpattern = re.compile(re.compile(r'\b{0}\b'.format(word), re.IGNORECASE))
    if category == 'name':
        nominees = findNomineesPerson(award, filteredTweets, pattern, keywords, targetpattern,
                                            min_matched,
                                            {},
                                            stop,
                                            False)
    #else:
        #nominee_dict = find_other_nominees(year, award, data, pattern, award_keywords, target_word_pattern,
         #                                  num_keywords_to_match_min, nominee_dict, category, stop_words, False)
    return nominees.keys()

nominee_dict = {}
for award in awards:
    nominee_dict[award] = findNominees(award)

def prepareJson():
    data2013 = { 
    "data": {
        "unstructured": {
            "hosts": [],
            "winners": [],
            "awards": [],
            "presenters": [],
            "nominees": []
        },
        "structured": {
            "Best Motion Picture - Drama": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Motion Picture - Comedy or Musical": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actor in a Motion Picture - Drama": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actor in a Motion Picture - Comedy or Musical": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actress in a Motion Picture - Drama": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actress in a Motion Picture - Comedy or Musical": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actor in a Supporting Role in a Motion Picture": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actress in a Supporting Role in a Motion Picture": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Director - Motion Picture": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Screenplay - Motion Picture": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Original Song - Motion Picture": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Original Score - Motion Picture": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Foreign Language Film": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Animated Film": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actor in a Television Series - Drama": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actor in a Mini-Series or a Motion Picture Made for Television": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actor in a Television Series - Musical or Comedy": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actress in a Television Series - Drama": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actress in a Mini-Series or a Motion Picture Made for Television": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actress in a Television Series - Musical or Comedy": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Television Series - Musical or Comedy": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Television Series - Drama": {
                "nominees": [],
                "winner": "",
                "presenters": []
            },
            "Best Mini-Series or Motion Picture Made for Television": {
                "nominees": [],
                "winner": "",
                "presenters": []
            }
        }
    }}
    if True:
        data2013['data']['unstructured']['hosts'] = hosts
        ####
        winnerList = []
        presenterList = []
        nomineeList = []
        for award in nominee_dict.keys():
            nomineeList.append(nominee_dict[award])
        ####
        data2013['data']['unstructured']['winners'] = winnerList
        data2013['data']['unstructured']['awards'] = awards
        data2013['data']['unstructured']['presenters'] = presenterList
        data2013['data']['unstructured']['nominees'] = nomineeList
        unknown = ["unknown"]
       # for awardIndex in range(0, 25):
        #	presentersList = []
        #	data2013['data']['structured'][allCategories[awardIndex]]["nominees"] = nominees_categorized[awardIndex]
        #	data2013['data']['structured'][allCategories[awardIndex]]["winner"] = winnerList[awardIndex]
        #	for key in presentersAward:
        #		if(presentersAward[key] == categories[awardIndex]):
        #			presentersList.append(key)
        #	if (len(presentersList) == 0):		
        #		data2013['data']['structured'][allCategories[awardIndex]]["presenters"] = unknown
        #	else:
        #		data2013['data']['structured'][allCategories[awardIndex]]["presenters"] = presentersList	
        with open('results.json', 'w') as outfile:
            json.dump(data2013, outfile)

