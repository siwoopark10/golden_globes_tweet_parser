from argparse import Namespace
import os
import re
import json
import string
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.util import ngrams
from nltk import ne_chunk
from nltk.tree import Tree
from collections import Counter
from nltk.corpus import stopwords
import imdb
from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class GoldenGlobesTweetParser:

    def read_tweets(self):
        cwd = os.getcwd()
        path = cwd + '\\gg2013.json'
        f = open(path)

        tweet_json = json.load(f)
        tweets = []
        for tweet in tweet_json:
            sentences = sent_tokenize(tweet['text'])

            for sentence in sentences:
                sentence = self.clean_sentence(sentence)
                tweets.append(sentence)

        self.tweets = tweets

    # used to get award winner name or title
    def personOrMovie(self, name):
        if name in self.visited:
            return self.visited[name]
        # print(name)
        people = self.ia.search_person(name)
        movies = self.ia.search_movie(name)

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
                self.visited[name] = person['name']
                return person['name']
            else:
                self.visited[name] = movie['title']
                return movie['title']
        else:
            return False


    # Used to get presenter name
    def personName(self, name):
        if name in self.presenter_visited:
            return self.presenter_visited[name]
        people = self.ia.search_person(name)

        person = people[0] if people else False

        match = similar(person['name'].lower(), name) if person else 0.0

        if match > 0.9:
            self.presenter_visited[name] = person['name']
            return person['name']
        else:
            return False


    def extract_winner(self, words_token):
        words = []
        for w in words_token:
            if w[1] == 'NNP':
                if not w[0].lower() in self.stop:
                    words.append(w[0].lower())
            else:
                break

        bigrams = ngrams(words,2)
        possible_names = Counter([])
        
        for bg in bigrams:
            temp = ' '.join(bg)
            possible_name = self.personOrMovie(temp)
            if possible_name:
                possible_names[possible_name] += 1
        if len(possible_names) > 0:
            return max(possible_names, key=possible_names.get)
        return False


    def extract_awards(self, words_token, name):
        words = []
        for w in words_token:
            if not w[0] in self.stop:
                if w[1] in self.award_words:
                    words.append(w[0])
                else:
                    break
        if len(words) == 2:
            possible_award = (words[0], words[1])
            # frequencies_award[possible_award] += 1
        elif len(words) >= 2:
            possible_award = (words[0], words[1])
            for i in range(2, min(5,len(words))):
                possible_award += (words[i],)
                # frequencies_award[possible_award] += 1
                self.possible_combos[(name, ' '.join(possible_award))] += 1
                # print((name, ' '.join(possible_award)))


    def analyze_sentence_for_winners(self, sentence, original_sentence):
        # if any win word is in the sentence
        for won in self.won_key_words:
            if won in sentence and 'best' in sentence:
                index_won = sentence.index(won)
                words_token = pos_tag(word_tokenize(original_sentence[:index_won]))
                name = self.extract_winner(words_token)
                
                if name:
                    index_best = sentence.index("best")
                    words_token = pos_tag(word_tokenize(sentence[index_best:]))
                    self.extract_awards(words_token, name)

                
        # reverse winner and award order
        for won in self.won_key_words_2:
            if won in sentence and 'best' in sentence:
                index_won = sentence.index(won)
                words_token = pos_tag(word_tokenize(original_sentence[index_won+len(won):]))
                name = self.extract_winner(words_token)
                
                if name:
                    index_best = sentence.index("best")
                    if index_best > index_won:
                        break
                    words_token = pos_tag(word_tokenize(sentence[index_best:index_won]))
                    self.extract_awards(words_token, name)


    def clean_sentence(self, sentence):
        sentence = re.sub(r"RT @.*: |http.*|\-", '', sentence)
        sentence = re.sub(r"\.|\/", ' ', sentence)
        
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            "]+", flags=re.UNICODE)

        sentence = emoji_pattern.sub(r'', sentence)

        return re.sub(r'\.', " ", sentence)


    def extract_presenters(self, words_token):
        words = []
        for w in words_token:
            if w[1] == 'NNP' and not w[0].lower() in self.stop:
                if w[0].lower() == 'best':
                    break
                words.append(w[0].lower())
        # print(words)

        bigrams = ngrams(words,2)
        possible_names = Counter([])
        
        for bg in bigrams:
            temp = ' '.join(bg)
            possible_name = self.personName(temp)
            if possible_name:
                possible_names[possible_name] += 1
        if len(possible_names) > 0:
            return tuple(possible_names.keys())
        return False

    def extract_awards_presenters(self, words_token, names):
        words = []
        for w in words_token:
            if not w[0].lower in self.stop:
                if w[1] in self.award_words:
                    words.append(w[0])
                else:
                    break
        if len(words) == 2:
            possible_award = (words[0], words[1])
            # frequencies_award[possible_award] += 1
        elif len(words) >= 2:
            possible_award = (words[0], words[1])
            for i in range(2, min(5,len(words))):
                possible_award += (words[i],)
                self.possible_presenter_combos[(names, ' '.join(possible_award))] += 1
                # print((names, ' '.join(possible_award)))

    def analyze_sentence_for_presenters(self, sentence, original_sentence):
        for present in self.present_key_words:
            if present in sentence and 'best' in sentence:
                # print(sentence)
                index_present = sentence.index(present)
                words_token = pos_tag(word_tokenize(original_sentence[:index_present]))
                names = self.extract_presenters(words_token)
                if names:
                    index_best = sentence.index("best")
                    words_token = pos_tag(word_tokenize(sentence[index_best:]))
                    self.extract_awards_presenters(words_token, names)
        
        # # reverse presenter award order
        for present in self.present_key_words_2:
            if present in sentence and 'best' in sentence:
                # print(sentence)
                index_present = sentence.index(present)
                words_token = pos_tag(word_tokenize(original_sentence[index_present+len(present):]))
                names = self.extract_presenters(words_token)
                # print(words_token)
                if names:
                    index_best = sentence.index("best")
                    # if index_best > index_won:
                    #     print("order messed up")
                    #     print(sentence)
                    #     break
                    words_token = pos_tag(word_tokenize(sentence[index_best:]))

                    self.extract_awards_presenters(words_token, names)

    # def output():


    def analyze_tweets(self):
        for tweet in self.tweets:

            self.analyze_sentence_for_winners(tweet.lower(), tweet[:])
        print(self.possible_combos)

        # analyze_sentence_for_presenters(sentence.lower(), sentence[:])
            
    def __init__(self):
        self.ia = imdb.Cinemagoer()
        self.won_key_words = ["wins", "win", "won","winning"]
        self.won_key_words_2 = ["goes to", "went to"]
        self.present_key_words = ["present", "presents", "presenting"]
        self.present_key_words_2 = ["presented by"]

        stop = {'golden', 'globes', 'globe', 'goldenglobes', 'goldenglobe', 'and', 
        'congrats', 'congratulations', 'yes','lol','yasssssssssss','Rt',"-", ''}
        possible_award_name_words = {'in', 'a', 'for', 'or'}
        stop.update(list(string.punctuation))
        stop.update(possible_award_name_words)
        self.stop = stop


        # types of tag awards names are a part of
        self.award_words = ['JJS', 'NNP', 'NN', 'VBG', 'VBD', 'JJ', 'VBD']

        self.possible_combos = Counter([])
        self.possible_presenter_combos = Counter([])

        self.presenter_visited = {}
        self.visited = {}


golden_globes_tweet_parser = GoldenGlobesTweetParser()
golden_globes_tweet_parser.read_tweets()
golden_globes_tweet_parser.analyze_tweets()




# a = clean_sentence('RT @sdkfjsdf: best.supporting actor👌')
# print(a)
# a = clean_sentence('best http://sdfsdf')
# print(a)
# a = clean_sentence('best/actor- tonight 🙏')
# print(a)
# a = clean_sentence('best actress janethevirgin 💕')
# print(a)