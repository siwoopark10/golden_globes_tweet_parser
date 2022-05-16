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


def read_tweets():
    cwd = os.getcwd()
    path = cwd + '\\gg2013.json'
    f = open(path)

    tweet_json = json.load(f)
    tweets = []
    for tweet in tweet_json:
        tweets.append(tweet["text"])
    return tweets

tweets = read_tweets()

won_key_words = ["wins", "win", "won"]
goes_to_key_words = ["goes to", "went to"]
stop_words = set(stopwords.words('english'))
additional_stop_words = {'golden', 'globes', 'goldenglobes'}
for word in additional_stop_words:
    stop_words.add(word)
stop = set(list(stop_words) + list(string.punctuation))

frequencies_winner = Counter([])
frequencies_award = Counter([])

for tweet in tweets[:50000]:
    sentences = sent_tokenize(tweet)

    for sentence in sentences:
        x = re.split("RT @.*: ", sentence)
        if len(x) > 1:
            sentence = x[1]
        for won in won_key_words:
            if won in sentence:
                index = sentence.index(won)
                words_token = word_tokenize(sentence[:index])
                words = [w for w in words_token if not w.lower() in stop]

                # unigrams = ngrams(words,1)
                # frequencies_winner += Counter(unigrams)
                bigrams = ngrams(words,2)
                frequencies_winner += Counter(bigrams)
                if "best" in sentence[len(word) + index:]:
                    index_best = sentence.index("best")
                    words_token = word_tokenize(sentence[index_best:])
                    words = []
                    for w in words_token:
                        if not w.lower() in stop and 'http' not in w:
                            words.append(w)
                    if len(words) == 2:
                        possible_award = (words[0], words[1])
                        frequencies_award[possible_award] += 1
                    elif len(words) >= 2:
                        possible_award = (words[0], words[1])
                        for i in range(2, min(5,len(words))):
                            possible_award += (words[i],)
                            frequencies_award[possible_award] += 1
                        # print(sentence)


                    
                    # bigrams = ngrams(words,2)
                    # trigrams = ngrams(words, 3)
                    # quadgrams = ngrams(words, 4)
                    # frequecies_award += Counter(bigrams)
                    # frequecies_award += Counter(trigrams)
                    # frequecies_award += Counter(quadgrams)
        
        # for keyword in goes_to_key_words:
        #     if keyword in sentence:
        #         index = sentence.index(won)
        #         words_token = word_tokenize(sentence[:index])
        #         words = [w for w in words_token if not w.lower() in stop]
        #         words = filter(lambda x:x[0]!='http', words)

        #         bigrams = ngrams(words,2)
        #         frequencies_winner += Counter(bigrams)
        #         if "best" in sentence[len(word) + index:]:
        #             index_best = sentence.index("best")
        #             words_token = word_tokenize(sentence[index_best:])
        #             words = [w for w in words_token if not w.lower() in stop]
        #             bigrams = ngrams(words,2)
        #             trigrams = ngrams(words, 3)
        #             quadgrams = ngrams(words, 4)
        #             frequecies_award += Counter(bigrams)
        #             frequecies_award += Counter(trigrams)
        #             frequecies_award += Counter(quadgrams)

frequencies_winner = {x: count for x, count in frequencies_winner.items() if count >= 3}
print(frequencies_winner)
print('   ')
frequencies_award = {x: count for x, count in frequencies_award.items() if count >= 3}
print(frequencies_award)