import snscrape.modules.twitter as sntwitter
import os
import csv
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
import contractions
import string
import pandas as pd

topic = "(ukraine OR ukrainian) (refugee OR (asylum seeker) OR migrant OR migration OR Immigrant OR immigration)"
num_of_tweets = 999
dates = "static/2022.csv"
time_sleep = 30


# Clean data
def preprocess(text):
    # TO LOWER CASE
    text = text.lower()

    # Fixes contractions such as "you're" to "you are"
    text = contractions.fix(text)

    # Remove URL
    text = re.sub(r"http\S+", " ", text)
    text = ''.join(i for i in text if i not in string.punctuation)  # Remove the punctuations
    text = ''.join([i for i in text if not i.isdigit()])  # Remove the numbers
    text = ' '.join(text.split())
    return text


def download_old_tweets():
    with open(dates) as file:
        reader = csv.reader(file)
        for row in reader:
            print("From: " + row[0] + " To: " + row[1])

            mysearch = f'{topic} -filter:retweets since:{row[0]} until:{row[1]} lang:"en" -filter:retweets -filter:links -filter:replies'
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(mysearch).get_items()):
                if i > num_of_tweets:
                    break

                text = preprocess(tweet.content)

                analyser = SentimentIntensityAnalyzer()
                score = analyser.polarity_scores(text)

                # ADD EXTRA COLUMN TO CSV (SENTIMENT ANALYSIS)
                analysis = ""

                if score['compound'] == 0:
                    analysis = "Neutral"
                elif 1 >= score['compound'] > 0:
                    analysis = "Positive"
                elif 0 > score['compound'] >= -1:
                    analysis = "Negative"

                # create dataframe
                columns = ['tweet_id',
                           'name',
                           'retweet_count',
                           'text',
                           'created_at',
                           'like_count',
                           'source_device',
                           'analysis',
                           'analysis_score']

                data = [[
                    tweet.id,
                    tweet.user.username,
                    tweet.retweetCount,
                    text,
                    tweet.date,
                    tweet.likeCount,
                    tweet.sourceLabel,
                    analysis,
                    score['compound']]]

                df = pd.DataFrame(data, columns=columns)

                output_path = 'csv/old_tweets.csv'
                df.to_csv(output_path, index=False, mode='a', header=not os.path.exists(output_path))

            time.sleep(time_sleep)  # WAIT (IN SECONDS)


def collect_old_tweets():
    download_old_tweets()

# DONE