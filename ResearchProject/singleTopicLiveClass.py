import pandas as pd
import tweepy
from textblob import TextBlob
import re
import collections
import csv
import datetime
import os
import app
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, jsonify, make_response
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tweepy import Stream
import json
from twitter_auth import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

positive = []
negative = []
neutral = []
sentiment_dict = {}


# Clean data
def preprocess(text):
    # Remove URL
    text = re.sub(r"http\S+", " ", text)
    text = re.sub('[^a-zA-Z0-9\'’!?]', ' ', text)
    text = ' '.join(text.split())
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

        # CREATE THE CSV FILE
        mined = {
            'tweet_id': data.id,
            'name': data.user.name,
            'retweet_count': data.retweet_count,
            'text': text,
            'created_at': data.created_at,
            'analysis': analysis,
            'analysis_score': score['compound']
        }

        create_csv_files(mined)
    else:
        print("IT WAS A RETWEET")


class Listener(tweepy.Stream):
    def on_status(self, data):
        analyze_tweets(data)
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
        global topic  # MAKE THE TOPIC A GLOBAL VARIABLE
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


def send_sentiment_data():
    return sentiment_dict


# STORE DATA IN A CSV FILE
def create_csv_files(mined):
    csv_exsits = os.path.exists(
        'static/CSV/singleTopic-{}.csv'.format(topic.replace(' OR ', "_").replace(' ', "-")))  # Check if CSV exists
    # Write to CSV file
    with open('static/CSV/singleTopic-{}.csv'.format(topic.replace(' OR ', "_").replace(' ', "-")), 'a', newline='',
              encoding="utf-8-sig") as outputFile:
        writer = csv.DictWriter(outputFile, mined.keys())

        # Using dictionary keys as Column name for the CSV file if CSV doesn't exists
        if not csv_exsits:
            writer.writeheader()

        writer.writerow(mined)
    outputFile.close()

# DONEEEE
