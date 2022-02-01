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
import matplotlib.pyplot as plt

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


def analyze_tweets(auth, topic, num_of_tweets):
    api = tweepy.API(auth, wait_on_rate_limit=True)
    downloaded_tweets = tweepy.Cursor(api.search_tweets, q="{} -filter:retweets -filter:links".format(topic),
                                      lang="en",
                                      tweet_mode='extended').items(num_of_tweets)

    for tweet in downloaded_tweets:
        text = preprocess(tweet.full_text)

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

        mined = {
            'tweet_id': tweet.id,
            'name': tweet.user.name,
            'retweet_count': tweet.retweet_count,
            'text': text,
            'created_at': tweet.created_at,
            'analysis': analysis,
            'analysis_score': score['compound']
        }

        create_csv_files(mined)

    # CREATE THE JSON FILES
    create_json_files_with_data()

    # PLOT A BAR CHART
    # bar_chart()

    # df = pd.DataFrame(text_list)
    # print(df.to_string())


def start_get_tweets(auth):
    if request.form['start_button'] == 'Start':
        create_empty_json_files()
        global topic  # MAKE THE TOPIC A GLOBAL VARIABLE
        global num_of_tweets  # MAKE THE Number A GLOBAL VARIABLE
        topic = request.form['first_query']
        num_of_tweets = int(request.form['second_query'])
        clear_arrays()
        analyze_tweets(auth, topic, num_of_tweets)
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
def create_json_files_with_data():
    # WRITE (POSITIVE, NEGATIVE, NEUTRAL) TO JSON FILE
    data = [['Analysis', 'positive', 'neutral', 'negative'],
            ['Number Of Tweets', str(sum(positive)), str(sum(neutral)), str(sum(negative))]]

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


# PLOT IN A BAR CHART
def bar_chart():
    x = ['Positive', 'Neutral', 'Negative']
    h = [sum(positive), sum(neutral), sum(negative)]
    c = ["blue", "grey", "green"]

    plt.bar(x, h, align='center', color=c)
    plt.xlabel("Sentiment")
    plt.ylabel('Number of Tweets')
    plt.title('The data is based around ({})'.format(topic))

    plt.savefig('static/staticData-{}.png'.format(topic))
    plt.show()

# DONEEEE
