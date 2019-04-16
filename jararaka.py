import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tweepy
import datetime
import json
from time import time, sleep
from polyglot.text import Text

consumer_key =
consumer_secret =
access_token =
access_token_secret =

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

user = api.me()
print(user.name)

keyw = ['Kariņ', 'Premjer', 'Valdīb', 'Ministr']


class MyStreamListener(tweepy.StreamListener):

    tweet_list = []
    counter = 0

    def plot_and_tweet(self, percent_list):

        labels = 'Pozitīvs', 'Negatīvs', 'Neitrāls'
        sizes = percent_list
        explode = (0.1, 0, 0,)

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.axis('equal')

        fig1 = plt.gcf()
        fig1.savefig('karin.png')

        # Tweets text with date & picture
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        api.update_with_media('valdiba.png',
                              'Twitter lietotāju viedoklis par Krišjāņa Kariņa valdību {}'.format(date))

    def percents(self, polarity_list):

        # Function to calculate percents of postive, negative and neutral tweets
        pos = neg = neut = c = 0
        percent_list = []

        for num in polarity_list:
            if num > 0:
                pos += 1
            elif num < 0:
                neg += 1
            else:
                neut += 1
            c += 1

            percent_list.append((pos / c) * 100)
            percent_list.append((neg / c) * 100)
            percent_list.append((neut / c) * 100)

            return percent_list

    def on_data(self, raw_data):

        # TODO try & except statements for error catching
        json_data = json.loads(raw_data)

        # Checks if tweet in json data is not retweet & is extended
        if json_data['user']['name'] != 'IkarBots':
            if 'RT' not in json_data:
                if 'extended_tweet' in json_data:
                    tweet = json_data['extended_tweet']['full_text']
                else:
                    tweet = json_data['text']

                self.tweet_list.append(tweet)
                self.counter += 1

                # Bot wil tweet after accumulating 50 tweets about Latvian gov.
                if self.counter > 50:
                    all_tweets = ' '
                    for i in self.tweet_list:
                        all_tweets += i

                    # Bot is using polyglot library to tokenize tweet text and to perform a polarity analysis on it
                    # Lists are emptied at the end
                    text = Text(all_tweets)
                    sent = text.sentences
                    polarity_list = [sentence.polarity for sentence in sent]

                    # Plot & tweet function is called & as argument takes list returned by percent calculator function
                    self.plot_and_tweet(self.percents(polarity_list))
                    self.tweet_list.clear()
                    self.counter = 0

    def on_error(self, status_code):
        if status_code == 420:
            print('Too many connections. Disconnecting...')
            return False

# Initialize Tweepy class methods to listen for tweets mentioning Latvian government
myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener, tweet_mode='extended')
myStream.filter(track=keyw)
