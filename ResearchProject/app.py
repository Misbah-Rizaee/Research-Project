from flask import Flask, render_template, request, jsonify, make_response
import tweepy
from twitter_auth import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
import staticDataClass
import singleTopicLiveClass
import aboutApplicationClass
import json
import os

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/static-data', methods=['GET', 'POST'])
def static_data_function():
    if request.method == "POST":
        staticDataClass.start_get_tweets(api)
        return '', 204
    else:
        return render_template('static-data.html')


# STATIC_DATA (DISPLAY POSITIVE, NEGATIVE, NEUTRAL IN LIVE CHART)
@app.route('/send_data_to_static_data', methods=['GET', 'POST'])
def send_data_to_static_data():
    if os.path.isfile("static/CSV/staticData1.json"):
        file = open("static/CSV/staticData1.json")
        data = json.load(file)
        file.close()

        response = make_response(json.dumps(data))
        response.content_type = 'application/json'
        return "Analysis,Positive, Neutral, Negative \n Number Of Tweets," + data[1][1] + "," + data[1][2] + "," + \
               data[1][3]
    else:
        print("File does not exist! FileNotFoundError has occurred")
        return '', 204


@app.route('/single-topic-live', methods=['GET', 'POST'])
def single_topic_live():
    if request.method == "POST":
        singleTopicLiveClass.start_streaming()
        return '', 204
    else:
        return render_template('single-topic-live.html')


# SINGLE-TOPIC-LIVE (DISPLAY POSITIVE, NEGATIVE, NEUTRAL IN LIVE CHART)
@app.route('/send_data_to_single_topic_live', methods=['GET', 'POST'])
def send_data_to_single_topic_live():
    if os.path.isfile("static/CSV/singleTopic1.json"):
        file = open("static/CSV/singleTopic1.json")
        data = json.load(file)
        file.close()

        response = make_response(json.dumps(data))
        response.content_type = 'application/json'
        return "Analysis,Positive, Neutral, Negative \n Number Of Tweets," + data[1][1] + "," + data[1][2] + "," + \
               data[1][3]
    else:
        print("File does not exist! FileNotFoundError has occurred")
        return '', 204


@app.route('/about-application')
def about_application():
    return render_template('about-application.html')


if __name__ == '__main__':
    app.run()

# DONEEE
