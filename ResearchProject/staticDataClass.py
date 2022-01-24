import pandas as pd
import tweepy
from textblob import TextBlob
import re
import collections
import csv
import datetime
import os
from flask import Flask, render_template, request, jsonify, make_response
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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

    text = re.sub(r'&amp', 'and', text); # &
    text = re.sub(r'&lt;', ' ', text); # <
    text = re.sub(r'&gt;', ' ', text); # >
    text = re.sub(r'&le;', ' ', text); # less-than or equals sign
    text = re.sub(r'&ge;', ' ', text); # greater-than or equals sign
    text = re.sub(r'\xa0', ' ', text); # non-breaking space

    return text


def analyze_tweets(api, topic, num_of_tweets):
    downloaded_tweets = tweepy.Cursor(api.search_tweets, q="{} -filter:retweets -filter:links".format(topic),
                                      lang="en",
                                      tweet_mode='extended').items(num_of_tweets)

    for tweet in downloaded_tweets:
        text = preprocess(tweet.full_text)

        analyser = SentimentIntensityAnalyzer()
        score = analyser.polarity_scores(text)

        if score['compound'] == 0:
            neutral.append(1)
        elif 1 >= score['compound'] > 0:
            positive.append(1)
        elif 0 > score['compound'] >= -1:
            negative.append(1)

        mined = {
            'tweet_id': tweet.id,
            'name': tweet.user.name,
            'screen_name': tweet.user.screen_name,
            'retweet_count': tweet.retweet_count,
            'text': text,
            'created_at': tweet.created_at,
            'favourite_count': tweet.favorite_count,
            'hashtags': tweet.entities['hashtags'],
            'status_count': tweet.user.statuses_count,
            'location': tweet.place,
            'source_device': tweet.source
        }

        create_csv_files(mined)

    # CREATE THE JSON FILES
    create_json_files_with_data(neutral, positive, negative)

    # df = pd.DataFrame(text_list)
    # print(df.to_string())


def start_get_tweets(api):
    if request.form['start_button'] == 'Start':
        create_empty_json_files()
        global topic  # MAKE THE TOPIC A GLOBAL VARIABLE
        global num_of_tweets  # MAKE THE Number A GLOBAL VARIABLE
        topic = request.form['first_query']
        num_of_tweets = int(request.form['second_query'])
        clear_arrays()
        analyze_tweets(api, topic, num_of_tweets)
    else:
        return render_template('static-data.html')


# WHEN SEARCHING NEW TOPIC, CLEAR ALL THE LISTS
def clear_arrays():
    positive.clear()
    negative.clear()
    neutral.clear()


# FIX - CREATE EMPTY JSON FILES TO AVOID (No such file or directory: 'static/CSV/staticData1.json') ERROR
def create_empty_json_files():
    # CREATE SAMPLE JSON FILE
    data = [['Analysis', 'positive', 'neutral', 'negative'],
            ['Number Of Tweets', str(0), str(0), str(0)]]

    with open("static/CSV/staticData1.json", "w") as outfile:
        json.dump(data, outfile)


# CREATE THE JSON FILES
def create_json_files_with_data(neu, pos, neg):
    # WRITE (POSITIVE, NEGATIVE, NEUTRAL) TO JSON FILE
    data = [['Analysis', 'positive', 'neutral', 'negative'],
            ['Number Of Tweets', str(sum(pos)), str(sum(neu)), str(sum(neg))]]

    with open("static/CSV/staticData1.json", "w") as outfile:
        json.dump(data, outfile)


# STORE DATA IN A CSV FILE
def create_csv_files(mined):
    csv_exsits = os.path.exists(
        'static/CSV/staticData-{}.csv'.format(topic.replace(' ', "-")))  # Check if CSV exists
    # Write to CSV file
    with open('static/CSV/staticData-{}.csv'.format(topic.replace(' ', "-")), 'a', newline='',
              encoding="utf-8-sig") as outputFile:
        writer = csv.DictWriter(outputFile, mined.keys())

        # Using dictionary keys as Column name for the CSV file if CSV doesn't exists
        if not csv_exsits:
            writer.writeheader()

        writer.writerow(mined)
    outputFile.close()

## DONEEEE
