from topic_modelling import topic_modelling
from tweepy_tweets import collect_tweets
from snscrape_tweets import collect_old_tweets
from word_cloud_class import word_cloud
from sentiment_analysis import sentiment_analysis


def main():
    # collect_tweets()
    # collect_old_tweets()
    # topic_modelling()
    word_cloud()
    # sentiment_analysis()


if __name__ == '__main__':
    main()