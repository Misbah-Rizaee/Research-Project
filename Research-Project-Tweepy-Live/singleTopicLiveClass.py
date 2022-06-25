import tweepy
import re
import app
import contractions
import string
import pandas as pd
from remove_emoji_class import remove_emoji

from flask import render_template, request
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from twitter_auth import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

# CREATE DATAFRAME FOR CSV
columns = ['tweet_id',
           'name',
           'screen_name',
           'retweet_count',
           'text',
           'created_at',
           'favourite_count',
           'hashtags',
           'status_count',
           'location',
           'source_device',
           'analysis',
           'analysis_score']
tweet_list = []

# TO SEND SENTIMENT DATA TO FRONTEND
positive = []
negative = []
neutral = []
sentiment_dict = {}


# Clean data
def preprocess(text):
    # TO LOWER CASE
    text = text.lower()

    # Fixes contractions such as "you're" to "you are"
    text = contractions.fix(text)

    text = re.sub(r"http\S+", " ", text)  # Remove URL
    text = ''.join(i for i in text if i not in string.punctuation)  # Remove the punctuations
    text = ''.join([i for i in text if not i.isdigit()])  # Remove the numbers
    text = ' '.join(text.split())
    text = remove_emoji(text)  # Remove emoji

    return text


# ANALYZING THE TWEETS
def analyze_tweets(data):
    if not data.truncated:
        text = data.text
    else:
        text = data.extended_tweet['full_text']

    # CHECK IF IT IS NOT RETWEET
    if not data.retweeted and 'RT @' not in text:
        text = preprocess(text)

        analyser = SentimentIntensityAnalyzer()
        score = analyser.polarity_scores(text)

        # ADD EXTRA COLUMN TO CSV (SENTIMENT ANALYSIS)
        analysis = ""

        if score['compound'] == 0:
            neutral.append(1)
            analysis = "Neutral"
        elif 1 >= score['compound'] > 0:
            positive.append(1)
            analysis = "Positive"
        elif 0 > score['compound'] >= -1:
            negative.append(1)
            analysis = "Negative"

        sentiment_dict['positive'] = sum(positive)
        sentiment_dict['neutral'] = sum(neutral)
        sentiment_dict['negative'] = sum(negative)

        tweet_list.append([
            data.id,
            data.user.name,
            data.user.screen_name,
            data.retweet_count,
            text,
            data.created_at,
            data.favorite_count,
            data.entities['hashtags'],
            data.user.statuses_count,
            data.place,
            data.source,
            analysis,
            score['compound']])

    else:
        print("IT WAS A RETWEET")


class Listener(tweepy.Stream):
    def on_status(self, data):
        analyze_tweets(data)

        # SAVE TWEETS IN CSV FILE
        df = pd.DataFrame(tweet_list, columns=columns)
        df.to_csv('csv/tweets.csv', index=False)

        # SEND SENTIMENT DATA TO app.py
        app.send_data_to_single_topic_live();
        return True

    def on_error(self, status_code):
        print(status_code)


twitterStream = Listener(
    API_KEY, API_SECRET,
    ACCESS_TOKEN, ACCESS_TOKEN_SECRET
)


def start_streaming():
    if request.form['submit_button'] == 'Start Stream':
        clear_arrays()
        global topic
        topic = request.form["query"]
        twitterStream.filter(track=[topic], languages=["en"])
    elif request.form['submit_button'] == 'Stop Stream':
        twitterStream.disconnect()
    else:
        return render_template('home.html')


# WHEN SEARCHING NEW TOPIC, CLEAR ALL THE LISTS
def clear_arrays():
    positive.clear()
    negative.clear()
    neutral.clear()
    sentiment_dict.clear()
    tweet_list.clear()


def send_sentiment_data():
    return sentiment_dict


# DONE
