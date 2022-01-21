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

positive = []
negative = []
neutral = []
text_list = []

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
    text = text.replace('\n', "")
    text = text.replace('\t', " ")

    return text


# Find the most occurred words
def words_occurrences(text_list):
    # Split the words of each tweet
    words_in_tweet = [text.lower().split() for text in text_list]

    excluded_topics = topic.split()
    joined_excluded_words = excluded_topics + excluded_words

    # List of all words across tweets
    all_words_in_tweet = [word for wordList in words_in_tweet for word in wordList if not word in joined_excluded_words]
    # Create counter
    counts = collections.Counter(all_words_in_tweet)
    # Get 5 most occurred words
    counts.most_common(5)

    return counts.most_common(5)


def analyze_tweets(api, topic, num_of_tweets):
    downloaded_tweets = tweepy.Cursor(api.search_tweets, q="{} -filter:retweets -filter:links".format(topic),
                                      lang="en",
                                      tweet_mode='extended').items(num_of_tweets)

    for tweet in downloaded_tweets:
        text = remove_url_emoji(tweet.full_text)

        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity

        if polarity == 0:
            neutral.append(1)
        elif 1 >= polarity > 0:
            positive.append(1)
        elif 0 > polarity >= -1:
            negative.append(1)

        # STORE TEXT IN A LIST (USED TO FIND MOST OCCURRED WORDS)
        text_list.append(re.sub(r"[-\"()#@;:.<>{}!?,]", "", text))

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

    # FIND 5 MOST OCCURRED WORDS
    most_occurred_words = words_occurrences(text_list)

    # CREATE THE JSON FILES
    create_json_files_with_data(neutral, positive, negative, most_occurred_words)

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
    text_list.clear()


# FIX - CREATE EMPTY JSON FILES TO AVOID (No such file or directory: 'static/CSV/staticData1.json') ERROR
def create_empty_json_files():
    # CREATE SAMPLE JSON FILE
    data = [['Analysis', 'positive', 'neutral', 'negative'],
            ['Number Of Tweets', str(0), str(0), str(0)]]

    with open("static/CSV/staticData1.json", "w") as outfile:
        json.dump(data, outfile)

    # CREATE SAMPLE2 JSON FILE
    data = [['Words', '1st Word', "2nd Word", "3rd Word", "4th Word", "5th Word"],
            ['Number Of Words', str(0), str(0), str(0), str(0), str(0)]]

    with open("static/CSV/staticData2.json", "w") as outfile:
        json.dump(data, outfile)


# # CREATE THE JSON FILES
def create_json_files_with_data(neu, pos, neg, most_occurred_words):
    # WRITE (POSITIVE, NEGATIVE, NEUTRAL) TO JSON FILE
    data = [['Analysis', 'positive', 'neutral', 'negative'],
            ['Number Of Tweets', str(sum(pos)), str(sum(neu)), str(sum(neg))]]

    with open("static/CSV/staticData1.json", "w") as outfile:
        json.dump(data, outfile)

    # WRITE (MOST OCCURRED WORDS) TO JSON FILE
    data = [['Words', most_occurred_words[0][0], most_occurred_words[1][0], most_occurred_words[2][0],
             most_occurred_words[3][0], most_occurred_words[4][0]],
            ['Number Of Words', str(most_occurred_words[0][1]), str(most_occurred_words[1][1]), str(
                most_occurred_words[2][1]), str(most_occurred_words[3][1]), str(most_occurred_words[4][1])]]

    with open("static/CSV/staticData2.json", "w") as outfile:
        json.dump(data, outfile)


# STORE DATA IN A CSV FILE
def create_csv_files(mined):
    csv_exsits = os.path.exists(
        'static/CSV/staticData-{}.csv'.format(topic.replace(' ', "-")))  # Check if CSV exists
    # Write to CSV file
    with open('static/CSV/staticData-{}.csv'.format(topic.replace(' ', "-")), 'a', newline='',
              encoding="utf-8") as outputFile:
        writer = csv.DictWriter(outputFile, mined.keys())

        # Using dictionary keys as Column name for the CSV file if CSV doesn't exists
        if not csv_exsits:
            writer.writeheader()

        writer.writerow(mined)
    outputFile.close()

## DONEEEEEEEEEEEEEEEEE
