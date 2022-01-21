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
words_in_tweet = []

excluded_words = ['a', 'an', 'on', 'in', 'to', 'under', 'behind', 'and', 'but', 'because', 'the', 'i', 'me', 'you',
                  'we', 'he', 'him', 'she', 'her', 'it', 'is', 'they', 'it', 'this', 'have', 'had', 'of', 'at',
                  'our', 'with', 'which', 'for', 'was', 'were', ';', 'has', 'by', 'are', 'if', 'so', 'when', 'that',
                  'who', 'not', 'from', 'like', 'his', 'as', 'all', 'do', 'did', 'just', 'be', '&amp', 'my', 'am',
                  'can', 'why', 'vs', 'no', 'yes', 'or', 'about', 'what', 'how', 'their', 'them', 'very',
                  'your', 'yours', 'would', 'will', 'now', 'should', 'always', 'one', 'two', 'three', 'more',
                  'most', 'please', 'these', 'those', 'didn\'t', 'don\'t', 'some', 'same', 'any', 'won\'t',
                  'wouldn\'t', 'you\'re', 'we\'re', 'it\'s', 'until', 'must', 'here', 'there', 'many', 'over', 'been',
                  'get', 'want', 'new', 'up', 'down', 'also', 'go', 'us', 'know', 'need']


# Remove URL and EMOJI from the tweets' text
def remove_url_emoji(text):
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

    # Remove \n and \t From the text
    text = text.replace('\n', " ")
    text = text.replace('\t', " ")

    return text


# Find the most occurred words
def words_occurrences(text):
    # Append text only to text_list
    text = re.sub(r"[-\"()#@;:.<>{}!?,]", "", text)  # Exclude Special Characters

    # Split the words of each tweet
    words_in_tweet.append(text.lower().split())

    excluded_topics = topic.split()
    joined_excluded_words = excluded_topics + excluded_words

    # List of all words across tweets
    all_words_in_tweet = [word for wordList in words_in_tweet for word in wordList if not word in joined_excluded_words]
    # Create counter
    counts = collections.Counter(all_words_in_tweet)
    # Get 5 most occurred words
    counts.most_common(5)

    return counts.most_common(5)


# ANALYZING THE TWEETS
def analyze_tweets(data, neu=neutral, pos=positive, neg=negative):
    if not data.truncated:
        text = data.text
    else:
        text = data.extended_tweet['full_text']

    # CHECK IF IT IS NOT RETWEET
    # if not data.retweeted and 'RT @' not in text:
    if not data.retweeted and 'RT @' not in text and len(check_length(remove_url_emoji(text))) >= 5:
        text = remove_url_emoji(text)

        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity

        if polarity == 0:
            neu.append(1)
        elif 1 >= polarity > 0:
            pos.append(1)
        elif 0 > polarity >= -1:
            neg.append(1)

        # FIND 5 MOST OCCURRED WORDS
        most_occurred_words = words_occurrences(text)

        # CREATE THE JSON FILES
        create_json_files_with_data(neu, pos, neg, most_occurred_words)

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
        app.send_data_to_single_topic_live_2();
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
    words_in_tweet.clear()


# FIX - CREATE EMPTY JSON FILES TO AVOID (No such file or directory: 'static/CSV/singleTopic1.json') ERROR
def create_empty_json_files():
    # CREATE SAMPLE JSON FILE
    data = [['Analysis', 'positive', 'neutral', 'negative'],
            ['Number Of Tweets', str(0), str(0), str(0)]]

    with open("static/CSV/singleTopic1.json", "w") as outfile:
        json.dump(data, outfile)

    # CREATE SAMPLE2 JSON FILE
    data = [['Words', '1st Word', "2nd Word", "3rd Word", "4th Word", "5th Word"],
            ['Number Of Words', str(0), str(0), str(0), str(0), str(0)]]

    with open("static/CSV/singleTopic2.json", "w") as outfile:
        json.dump(data, outfile)


# # CREATE THE JSON FILES
def create_json_files_with_data(neu, pos, neg, most_occurred_words):
    # WRITE (POSITIVE, NEGATIVE, NEUTRAL) TO JSON FILE
    data = [['Analysis', 'positive', 'neutral', 'negative'],
            ['Number Of Tweets', str(sum(pos)), str(sum(neu)), str(sum(neg))]]

    with open("static/CSV/singleTopic1.json", "w") as outfile:
        json.dump(data, outfile)

    # WRITE (MOST OCCURRED WORDS) TO JSON FILE
    data = [['Words', most_occurred_words[0][0], most_occurred_words[1][0], most_occurred_words[2][0],
             most_occurred_words[3][0], most_occurred_words[4][0]],
            ['Number Of Words', str(most_occurred_words[0][1]), str(most_occurred_words[1][1]), str(
                most_occurred_words[2][1]), str(most_occurred_words[3][1]), str(most_occurred_words[4][1])]]

    with open("static/CSV/singleTopic2.json", "w") as outfile:
        json.dump(data, outfile)


# STORE DATA IN A CSV FILE
def create_csv_files(mined):
    csv_exsits = os.path.exists(
        'static/CSV/singleTopic-{}.csv'.format(topic.replace(' ', "-")))  # Check if CSV exists
    # Write to CSV file
    with open('static/CSV/singleTopic-{}.csv'.format(topic.replace(' ', "-")), 'a', newline='',
              encoding="utf-8") as outputFile:
        writer = csv.DictWriter(outputFile, mined.keys())

        # Using dictionary keys as Column name for the CSV file if CSV doesn't exists
        if not csv_exsits:
            writer.writeheader()

        writer.writerow(mined)
    outputFile.close()


# FIX - CHECK TWEET TEXT LENGTH WITHOUT EXCLUDED WORDS TO AVOID (list index out of range handle) ERROR
def check_length(text):
    # Append text only to text_list
    text = re.sub(r"[-\"()#@;:.<>{}!?,]", "", text)  # Exclude Special Characters

    # Split the words of each tweet
    words_in_tweet_check_length = text.lower().split()

    excluded_topics = topic.split()
    joined_excluded_words = excluded_topics + excluded_words

    # List of all words across tweets
    all_words_in_tweet = [word for word in words_in_tweet_check_length if not word in joined_excluded_words]

    return all_words_in_tweet

# DONEEEEEEEEEEEEEEEEEE
