import os
import re
import json
import string
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.util import ngrams
from collections import Counter
from nltk.corpus import stopwords
import imdb
from difflib import SequenceMatcher


ia = imdb.Cinemagoer()


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def read_tweets():
    cwd = os.getcwd()
    path = cwd + '\\gg2013.json'
    f = open(path)

    tweet_json = json.load(f)
    tweets = []
    for tweet in tweet_json:
        tweets.append(tweet["text"])
    return tweets



won_key_words = ["wins", "win", "won","winning"]
won_key_words_2 = ["goes to", "went to"]



stop = {'golden', 'globes', 'goldenglobes'}
possible_award_name_words = {'in', 'a', 'for', 'or'}
stop.update(list(string.punctuation))
stop.update(possible_award_name_words)
print(stop)


# types of tag awards names are a part of
award_words = ['JJS', 'NNP', 'NN', 'VBG', 'VBD', 'JJ', 'VBD']

frequencies_winner = Counter([])
frequencies_award = Counter([])
possible_combos = Counter([])

def personOrMovie(name):
    people = ia.search_person(name)
    movies = ia.search_movie(name)

    person = people[0] if people else False
    movie = movies[0] if movies else False

    person_match = similar(person['name'].lower(), name) if person else 0.0
    movie_match_l = similar(
        movie['long imdb title'].lower(), name) if movie else 0.0
    movie_match_s = similar(movie['title'].lower(), name) if movie else 0.0
    movie_match_avg = (movie_match_l + movie_match_s) / 2

    match = max(movie_match_avg, person_match)
    if match > 0.55:
        if person_match >= movie_match_avg:
            return person['name']
        else:
            return movie['title']
    else:
        return False


def analyze_tweets():
    for i,tweet in enumerate(tweets):
        if i % 5000 == 0:
            print(i)
            print(possible_combos)
        sentences = sent_tokenize(tweet)

        for sentence in sentences:
            sentence = sentence.lower()
            x = re.split("rt @.*: ", sentence)
            if len(x) > 1:
                sentence = x[1]
            x = re.split("http.*", sentence)
            if len(x) > 1:
                sentence = ' '.join(x)

            # if any win word is in the sentence
            for won in won_key_words:
                if won in sentence and 'best' in sentence:
                    index_won = sentence.index(won)
                    words_token = word_tokenize(sentence[:index_won])
                    words = []
                    for w in words_token:
                        # if w[1] == 'NNP':
                        if not w in stop:
                            words.append(w)

                    bigrams = ngrams(words,2)
                    possible_names = Counter([])
                    name = ''
                    
                    # frequencies_winner += Counter(bigrams)
                    for bg in bigrams:
                        temp = ' '.join(bg)
                        possible_name = personOrMovie(temp)
                        if possible_name:
                            possible_names[possible_name] += 1
                    if len(possible_names) > 0:
                        name = max(possible_names, key=possible_names.get)
                    
                        index_best = sentence.index("best")
                        words_token = pos_tag(word_tokenize(sentence[index_best:]))

                        words = []
                        for w in words_token:
                            if not w[0] in stop:
                                if w[1] in award_words:
                                    words.append(w[0])
                                else:
                                    break
                        if len(words) == 2:
                            possible_award = (words[0], words[1])
                            frequencies_award[possible_award] += 1
                        elif len(words) >= 2:
                            possible_award = (words[0], words[1])
                            for i in range(2, min(5,len(words))):
                                possible_award += (words[i],)
                                # frequencies_award[possible_award] += 1
                                possible_combos[(name, ' '.join(possible_award))] += 1
                                # print((name, ' '.join(possible_award)))
            
            # reverse winner and award order
            for won in won_key_words_2:
                if won in sentence and 'best' in sentence:
                    index_won = sentence.index(won)
                    words_token = word_tokenize(sentence[index_won+len(won):])
                    words = []
                    for w in words_token:
                        # if w[1] == 'NNP':
                        if not w in stop:
                            words.append(w)

                    bigrams = ngrams(words,2)
                    possible_names = Counter([])
                    name = ''
                    
                    # frequencies_winner += Counter(bigrams)
                    for bg in bigrams:
                        temp = ' '.join(bg)
                        possible_name = personOrMovie(temp)
                        if possible_name:
                            possible_names[possible_name] += 1
                    if len(possible_names) > 0:
                        name = max(possible_names, key=possible_names.get)
                    
                        index_best = sentence.index("best")
                        if index_best > index_won:
                            print("order messed up")
                            print(sentence)
                            break
                        words_token = pos_tag(word_tokenize(sentence[index_best:index_won]))

                        words = []
                        for w in words_token:
                            if not w[0] in stop:
                                if w[1] in award_words:
                                    words.append(w[0])
                                else:
                                    break
                        if len(words) == 2:
                            possible_award = (words[0], words[1])
                            frequencies_award[possible_award] += 1
                        elif len(words) >= 2:
                            possible_award = (words[0], words[1])
                            for i in range(2, min(5,len(words))):
                                possible_award += (words[i],)
                                # frequencies_award[possible_award] += 1
                                possible_combos[(name, ' '.join(possible_award))] += 1
                                # print((name, ' '.join(possible_award)))
    print(possible_combos)
                                

tweets = read_tweets()
analyze_tweets()


