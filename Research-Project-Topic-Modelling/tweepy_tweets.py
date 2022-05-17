import tweepy
from twitter_auth import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
import pandas as pd
import re
import string
import contractions
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

title = "ukrainian refugees"
num = 20


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

def collect_tweets():
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    api = tweepy.API(auth, wait_on_rate_limit=True)
    tweets = tweepy.Cursor(api.search_tweets, q="{} -filter:retweets -filter:links".format(title),
                                  lang="en",
                                  tweet_mode='extended').items(num)

    # create dataframe
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
    for tweet in tweets:
        text = preprocess(tweet.full_text)

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

        tweet_list.append([
            tweet.id,
            tweet.user.name,
            tweet.user.screen_name,
            tweet.retweet_count,
            text,
            tweet.created_at,
            tweet.favorite_count,
            tweet.entities['hashtags'],
            tweet.user.statuses_count,
            tweet.place,
            tweet.source,
            analysis,
            score['compound']])

    df = pd.DataFrame(tweet_list, columns=columns)

    df.to_csv('csv/tweets.csv', index=False)

# DONE