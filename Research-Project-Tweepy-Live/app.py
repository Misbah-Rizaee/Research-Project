from flask import Flask, render_template, request
import tweepy
from twitter_auth import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
import singleTopicLiveClass


auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


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


if __name__ == '__main__':
    app.run()

# DONE
