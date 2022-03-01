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
import app

sentiment_dict = {}
retweet_dict = {}
created_at_list = []
analysis_score_list = []

def get_sentiments(data):
    # JSON FORMAT
    sentAnalysis = json.loads(data.analysis.value_counts().to_json())

    for key, value in sentAnalysis.items():
        sentiment_dict[key] = value


def get_sum_retweets(data):
    data['created_at'] = pd.to_datetime(data['created_at'])

    # GET SUM OF RETWEETS
    retweet_sum = data.groupby(pd.Grouper(key='analysis'))['retweet_count'].sum().dropna().reset_index()

    values = retweet_sum['analysis'].unique()
    retweet_sum.set_index("analysis", inplace=True)
    for i in values:
        retweet_dict[i] = retweet_sum.loc[i]['retweet_count']


def get_weekly_sentiment(data):
    data['created_at'] = pd.to_datetime(data['created_at'])

    # GET MEAN OF ANALYSIS SCORE
    weekly_mean = data.groupby(pd.Grouper(key='created_at', freq='W'))['analysis_score'].mean().dropna().reset_index()

    # REMOVE TIME SERIES
    weekly_mean['created_at'] = weekly_mean['created_at'].dt.date

    weekly_mean['created_at'] = range(1, 1 + len(weekly_mean))

    created_at_list.append(weekly_mean['created_at'].tolist())
    analysis_score_list.append(weekly_mean['analysis_score'].tolist())


def send_sentiment_data():
    return sentiment_dict


def send_retweet_data():
    return retweet_dict


def send_average_sentiment_data():
    return created_at_list, analysis_score_list


def clear_dict():
    sentiment_dict.clear()
    retweet_dict.clear()
    created_at_list.clear()
    analysis_score_list.clear()

def start_analysing(data):
    clear_dict()
    get_sentiments(data)
    get_sum_retweets(data)
    get_weekly_sentiment(data)

# DONEEE