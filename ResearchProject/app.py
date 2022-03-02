from flask import Flask, render_template, request, jsonify, make_response
import tweepy
from twitter_auth import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
import staticDataClass
import singleTopicLiveClass
import aboutApplicationClass
import json
import os
import pandas as pd

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


# STATIC DATA
@app.route('/static-data', methods=['GET', 'POST'])
def static_data_function():
    if request.method == "POST":
        staticDataClass.start_get_tweets(auth)
        return '', 204
    else:
        return render_template('static-data.html')


@app.route('/send_data_to_static_data', methods=['GET', 'POST'])
def send_data_to_static_data():
    send_data = staticDataClass.send_sentiment_data()
    # SORT THE DICTIONARY ITEMS
    send_data = dict(sorted(send_data.items()))

    # GET ONLY KEYS AND VALUES FROM THE DICTIONARY SEPARATED BY COMMA
    send_data_key = ', '.join([str(elem) for elem in send_data.keys()])
    send_data_value = ', '.join([str(elem) for elem in send_data.values()])

    if not send_data:
        return '', 204
    else:
        return "Analysis, " + send_data_key + "\n Numbers," + send_data_value


# SINGLE TOPIC LIVE
@app.route('/single-topic-live', methods=['GET', 'POST'])
def single_topic_live():
    if request.method == "POST":
        singleTopicLiveClass.start_streaming()
        return '', 204
    else:
        return render_template('single-topic-live.html')


@app.route('/send_data_to_single_topic_live', methods=['GET', 'POST'])
def send_data_to_single_topic_live():
    send_data = singleTopicLiveClass.send_sentiment_data()
    # SORT THE DICTIONARY ITEMS
    send_data = dict(sorted(send_data.items()))

    # GET ONLY KEYS AND VALUES FROM THE DICTIONARY SEPARATED BY COMMA
    send_data_key = ', '.join([str(elem) for elem in send_data.keys()])
    send_data_value = ', '.join([str(elem) for elem in send_data.values()])

    if not send_data:
        return '', 204
    else:
        return "Analysis, " + send_data_key + "\n Numbers," + send_data_value


# ABOUT APPLICATION
@app.route('/about-application', methods=['GET', 'POST'])
def about_application():
    if request.method == 'POST':
        file = request.form['input-file']
        target = os.path.join(app.static_folder, file)
        data = pd.read_csv(target)
        aboutApplicationClass.start_analysing(data)
        return '', 204
    else:
        return render_template('about-application.html')


@app.route('/send_sentiment_data_to_about_application', methods=['GET', 'POST'])
def send_sentiment_data_to_about_application():
    send_data = aboutApplicationClass.send_sentiment_data()
    # SORT THE DICTIONARY ITEMS
    send_data = dict(sorted(send_data.items()))

    # GET ONLY KEYS AND VALUES FROM THE DICTIONARY SEPARATED BY COMMA
    send_data_key = ', '.join([str(elem) for elem in send_data.keys()])
    send_data_value = ', '.join([str(elem) for elem in send_data.values()])

    if not send_data:
        return '', 204
    else:
        return "Analysis, " + send_data_key + "\n Numbers," + send_data_value


@app.route('/send_retweet_data_to_about_application', methods=['GET', 'POST'])
def send_retweet_data_to_about_application():
    send_data = aboutApplicationClass.send_retweet_data()
    # SORT THE DICTIONARY ITEMS
    send_data = dict(sorted(send_data.items()))

    # GET ONLY KEYS AND VALUES FROM THE DICTIONARY SEPARATED BY COMMA
    send_data_key = ', '.join([str(elem) for elem in send_data.keys()])
    send_data_value = ', '.join([str(elem) for elem in send_data.values()])

    if not send_data:
        return '', 204
    else:
        return "Analysis, " + send_data_key + "\n Numbers," + send_data_value


@app.route('/send_average_data_to_about_application', methods=['GET', 'POST'])
def send_average_data_to_about_application():
    send_data_key, send_data_value = aboutApplicationClass.send_average_sentiment_data()

    # GET ONLY KEYS AND VALUES FROM THE LIST SEPARATED BY COMMA
    send_data_key = ', '.join([str(elem) for elem in send_data_key])
    send_data_value = ', '.join([str(elem) for elem in send_data_value])

    if not send_data_key and send_data_value:
        return '', 204
    else:
        return "Analysis, " + str(send_data_key)[1:-1] + "\n Numbers," + str(send_data_value)[1:-1]


@app.route('/send_GPE_data_to_about_application', methods=['GET', 'POST'])
def send_GPE_data_to_about_application():
    send_data = aboutApplicationClass.send_GPE_name_entity_data()

    # GET ONLY KEYS AND VALUES FROM THE DICTIONARY SEPARATED BY COMMA
    send_data_key = ', '.join([str(elem) for elem in send_data.keys()])
    send_data_value = ', '.join([str(elem) for elem in send_data.values()])

    if not send_data:
        return '', 204
    else:
        return "Analysis, " + send_data_key + "\n Numbers," + send_data_value


@app.route('/send_NORP_data_to_about_application', methods=['GET', 'POST'])
def send_NORP_data_to_about_application():
    send_data = aboutApplicationClass.send_NORP_name_entity_data()

    # GET ONLY KEYS AND VALUES FROM THE DICTIONARY SEPARATED BY COMMA
    send_data_key = ', '.join([str(elem) for elem in send_data.keys()])
    send_data_value = ', '.join([str(elem) for elem in send_data.values()])

    if not send_data:
        return '', 204
    else:
        return "Analysis, " + send_data_key + "\n Numbers," + send_data_value


if __name__ == '__main__':
    app.run()

# DONEE
