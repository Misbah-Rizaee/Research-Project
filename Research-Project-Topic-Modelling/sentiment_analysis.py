import json
import numpy
import pandas as pd
import matplotlib.pyplot as plt


def value_label_graph(x_list, y_list):
    for i in range(len(x_list)):
        # plt.text(i, y_list[i], y_list[i], ha="center")
        plt.text(i, y_list[i] / 2, y_list[i], ha="center")


def normal_sentiment(data):
    # JSON FORMAT
    sent_analysis = json.loads(data.analysis.value_counts().to_json())

    x = ['Positive', 'Neutral', 'Negative']
    # RETURNS 0 IF THE VALUE IS MISSING
    h = [sent_analysis.get('Positive', 0), sent_analysis.get('Neutral', 0), sent_analysis.get('Negative', 0)]
    c = [numpy.random.rand(3, ), numpy.random.rand(3, ), numpy.random.rand(3, )]

    plt.bar(x, h, align='center', color=c, alpha=0.5)
    plt.xlabel("Sentiment status")
    plt.ylabel('Number of Tweets')
    plt.title('Sentiment status of the tweets')
    plt.grid(axis='y')
    value_label_graph(x, h)
    plt.savefig('result/Sentiment-Analysis.png')
    plt.show()


def sum_retweets_sentiment(data):
    # GET SUM OF RETWEETS
    retweet_sum = data.groupby(pd.Grouper(key='analysis'))['retweet_count'].sum().dropna().reset_index()
    retweet_sum.set_index("analysis", inplace=True)

    # PLOT THE ANALYSIS SCORE
    x = ['Positive', 'Neutral', 'Negative']
    h = [retweet_sum.loc['Positive']['retweet_count'], retweet_sum.loc['Neutral']['retweet_count'],
         retweet_sum.loc['Negative']['retweet_count']]
    c = [numpy.random.rand(3, ), numpy.random.rand(3, ), numpy.random.rand(3, )]
    plt.bar(x, h, align='center', color=c, alpha=0.5)
    plt.xlabel("Sentiment status")
    plt.ylabel('Sum of retweets')
    plt.title('Sum of retweets per Sentiment status')
    plt.grid(axis='y')
    value_label_graph(x, h)
    plt.savefig('result/Sentiment-Sum-Retweets.png', bbox_inches='tight')
    plt.show()


def sentiment_analysis():

    data = pd.read_csv("csv/old_tweets.csv")

    # NORMAL SENTIMENT
    normal_sentiment(data)

    # SUM RETWEETS PER SENTIMENT
    sum_retweets_sentiment(data)


# DONEE