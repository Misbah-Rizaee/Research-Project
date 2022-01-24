import pandas as pd
import tweepy
from textblob import TextBlob
import re
import collections
import csv
import datetime
import os
import app

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
    text = re.sub(r'https://t.co/\w{10}', '', text)

    # Remove EMOJI
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)

    text = text.replace('\n', " ")
    text = text.replace('\t', " ")

    # UTF-8 characters
    text = re.sub(r"Â", "", text);
    text = re.sub(r"â€™", "'", text);
    text = re.sub(r"â€œ", '"', text);
    text = re.sub(r'â€“', '-', text);
    text = re.sub(r'â€', '"', text);

    text = re.sub(r'&amp', 'and', text);  # &
    text = re.sub(r'&lt;', ' ', text);  # <
    text = re.sub(r'&gt;', ' ', text);  # >
    text = re.sub(r'&le;', ' ', text);  # less-than or equals sign
    text = re.sub(r'&ge;', ' ', text);  # greater-than or equals sign
    text = re.sub(r'\xa0', ' ', text);  # non-breaking space

    return text


# ANALYZING THE TWEETS
def analyze_tweets(data, neu=neutral, pos=positive, neg=negative):
    if not data.truncated:
        text = data.text
    else:
        text = data.extended_tweet['full_text']

    # CHECK IF IT IS NOT RETWEET
    if not data.retweeted and 'RT @' not in text:
        text = preprocess(text)

        analyser = SentimentIntensityAnalyzer()
        score = analyser.polarity_scores(text)

        if score['compound'] == 0:
            neutral.append(1)
        elif 1 >= score['compound'] > 0:
            positive.append(1)
        elif 0 > score['compound'] >= -1:
            negative.append(1)

        # CREATE THE JSON FILES
        create_json_files_with_data(neu, pos, neg)

        # CREATE THE CSV FILE
        mined = {
            'tweet_id': data.id,
            'name': data.user.name,
            'screen_name': data.user.screen_name,
            'retweet_count': data.retweet_count,
            'text': text,
            'created_at': data.created_at,
            'favourite_count': data.favorite_count,
            'hashtags': data.entities['hashtags'],
            'status_count': data.user.statuses_count,
            'location': data.place,
            'source_device': data.source
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
def create_json_files_with_data(neu, pos, neg):
    # WRITE (POSITIVE, NEGATIVE, NEUTRAL) TO JSON FILE
    data = [['Analysis', 'positive', 'neutral', 'negative'],
            ['Number Of Tweets', str(sum(pos)), str(sum(neu)), str(sum(neg))]]

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


# DONEEEE
