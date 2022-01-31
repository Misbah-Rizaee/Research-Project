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

        # CREATE THE JSON FILES
        create_json_files_with_data()

        # CREATE THE CSV FILE
        mined = {
            'tweet_id': data.id,
            'name': data.user.name,
            'retweet_count': data.retweet_count,
            'text': text,
            'created_at': data.created_at,
            'Analysis': analysis
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
        create_empty_json_files()
        global topic  # MAKE THE TOPIC A GLOBAL VARIABLE
        topic = request.form["query"]
        clear_arrays()
        twitterStream.filter(track=[topic], languages=["en"])
    elif request.form['submit_button'] == 'Stop Stream':
        twitterStream.disconnect()
        # PLOT A BAR CHART
        bar_chart()
    else:
        return render_template('home.html')


# WHEN SEARCHING NEW TOPIC, CLEAR ALL THE LISTS
def clear_arrays():
    positive.clear()
    negative.clear()
    neutral.clear()


# FIX - CREATE EMPTY JSON FILES TO AVOID (No such file or directory: 'static/CSV/singleTopic1.json') ERROR
def create_empty_json_files():
    # CREATE SAMPLE JSON FILE
    data = [['Analysis', 'positive', 'neutral', 'negative'],
            ['Number Of Tweets', str(0), str(0), str(0)]]

    with open("static/CSV/singleTopic1.json", "w") as outfile:
        json.dump(data, outfile)


# CREATE THE JSON FILES
def create_json_files_with_data():
    # WRITE (POSITIVE, NEGATIVE, NEUTRAL) TO JSON FILE
    data = [['Analysis', 'positive', 'neutral', 'negative'],
            ['Number Of Tweets', str(sum(positive)), str(sum(neutral)), str(sum(negative))]]

    with open("static/CSV/singleTopic1.json", "w") as outfile:
        json.dump(data, outfile)


# STORE DATA IN A CSV FILE
def create_csv_files(mined):
    csv_exsits = os.path.exists(
        'static/CSV/singleTopic-{}.csv'.format(topic.replace(' ', "-")))  # Check if CSV exists
    # Write to CSV file
    with open('static/CSV/singleTopic-{}.csv'.format(topic.replace(' ', "-")), 'a', newline='',
              encoding="utf-8-sig") as outputFile:
        writer = csv.DictWriter(outputFile, mined.keys())

        # Using dictionary keys as Column name for the CSV file if CSV doesn't exists
        if not csv_exsits:
            writer.writeheader()

        writer.writerow(mined)
    outputFile.close()


# PLOT IN A BAR CHART
def bar_chart():
    x = ['Positive', 'Neutral', 'Negative']
    h = [sum(positive), sum(neutral), sum(negative)]
    c = ["blue", "grey", "green"]

    plt.bar(x, h, align='center', color=c)
    plt.xlabel("Sentiment")
    plt.ylabel('Number of Tweets')
    plt.title('The data is based around ({})'.format(topic))

    plt.savefig('static/singleTopic-{}.png'.format(topic))
    plt.show()

# DONEEE
