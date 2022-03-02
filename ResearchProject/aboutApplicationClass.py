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
import numpy
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

sentiment_dict = {}
retweet_dict = {}
created_at_list = []
analysis_score_list = []

list_ORG = []
list_PERSON = []
list_GPE = []
list_NORP = []
list_EVENT = []

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


def get_name_entity(data):
    data.dropna(inplace=True)
    # LIST OF LISTS
    text = [text.lower() for text in data["text"]]

    # SPLIT THE LISTS TO PARTS
    if 1 <= len(text) <= 20000:
        splited_list = numpy.array_split(text, 20)
        print(20)
    elif 20001 <= len(text) <= 40000:
        splited_list = numpy.array_split(text, 40)
        print(40)
    elif 40001 <= len(text) <= 60000:
        splited_list = numpy.array_split(text, 60)
        print(60)
    elif 60001 <= len(text) <= 80000:
        splited_list = numpy.array_split(text, 80)
        print(80)
    elif 80001 <= len(text) <= 100000:
        splited_list = numpy.array_split(text, 100)
        print(100)
    elif 100001 <= len(text) <= 200000:
        splited_list = numpy.array_split(text, 200)
        print(200)
    elif 200001 <= len(text):
        splited_list = numpy.array_split(text, 300)
        print(300)

    for i in splited_list:
        # LIST OF TWEETS TO STRING SEPARATED BY DOT
        joined_text = ". ".join(i)

        nlp_text = nlp(joined_text)

        # FOR EACH WORD IN TEXT
        for entity in nlp_text.ents:
            if entity.label_ == "ORG":
                list_ORG.append(entity.text)
            if entity.label_ == "PERSON":
                list_PERSON.append(entity.text)
            if entity.label_ == "GPE":
                list_GPE.append(entity.text)
            if entity.label_ == "NORP":
                list_NORP.append(entity.text)
            if entity.label_ == "EVENT":
                list_EVENT.append(entity.text)


def send_sentiment_data():
    return sentiment_dict


def send_retweet_data():
    return retweet_dict


def send_average_sentiment_data():
    return created_at_list, analysis_score_list


def send_ORG_name_entity_data():
    counter_ORG = Counter(list_ORG)
    most_occur_ORG = dict(counter_ORG.most_common(10))
    return most_occur_ORG


def send_PERSON_name_entity_data():
    counter_PERSON = Counter(list_PERSON)
    most_occur_PERSON = dict(counter_PERSON.most_common(10))
    return most_occur_PERSON


def send_GPE_name_entity_data():
    counter_GPE = Counter(list_GPE)
    most_occur_GPE = dict(counter_GPE.most_common(10))
    return most_occur_GPE


def send_NORP_name_entity_data():
    counter_NORP = Counter(list_NORP)
    most_occur_NORP = dict(counter_NORP.most_common(10))
    return most_occur_NORP


def send_EVENT_name_entity_data():
    counter_EVENT = Counter(list_EVENT)
    most_occur_EVENT = dict(counter_EVENT.most_common(10))
    return most_occur_EVENT


def clear_dict():
    sentiment_dict.clear()
    retweet_dict.clear()
    created_at_list.clear()
    analysis_score_list.clear()

    list_ORG.clear()
    list_PERSON.clear()
    list_GPE.clear()
    list_NORP.clear()
    list_EVENT.clear()


def start_analysing(data):
    clear_dict()
    get_sentiments(data)
    get_sum_retweets(data)
    get_weekly_sentiment(data)
    get_name_entity(data)

# DONEEE