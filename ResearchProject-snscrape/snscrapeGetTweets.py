import snscrape.modules.twitter as sntwitter
import os
import csv
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time

tweets_list2 = []


topic = "(refugee OR refugees) camp"
# topic = "(blue OR red) (milan OR inter)"
num_of_tweets = 499  # 50 tweets

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


# STORE DATA IN A CSV FILE
def create_csv_files(mined):
    csv_exsits = os.path.exists(
        'static/staticData-{}.csv'.format(topic.replace(' OR ', "-").replace(' ', "-")))  # Check if CSV exists
    # Write to CSV file
    with open('static/staticData-{}.csv'.format(topic.replace(' OR ', "-").replace(' ', "-")), 'a', newline='',
              encoding="utf-8-sig") as outputFile:
        writer = csv.DictWriter(outputFile, mined.keys())

        # Using dictionary keys as Column name for the CSV file if CSV doesn't exists
        if not csv_exsits:
            writer.writeheader()

        writer.writerow(mined)
    outputFile.close()


def download_old_tweets():
    with open("static/Yearly/2021.csv") as file:
        reader = csv.reader(file)
        for row in reader:
            print("From: "+row[0]+" To: "+row[1])

            # GET OLD TWEETS
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
                    'name': tweet.user.username,
                    'retweet_count': tweet.retweetCount,
                    'text': text,
                    'created_at': tweet.date,
                    'analysis': analysis,
                    'analysis_score': score['compound']
                }

                create_csv_files(mined)

            time.sleep(61)  # SECOND

download_old_tweets()

# DONEEEE
