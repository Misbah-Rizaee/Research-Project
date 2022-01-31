import snscrape.modules.twitter as sntwitter
import os
import csv

tweets_list2 = []

# topic = "afghanistan refugee"
# topic = "global warming"
topic = "biden america"


# STORE DATA IN A CSV FILE
def create_csv_files(mined):
    csv_exsits = os.path.exists(
        'static/staticData-{}.csv'.format(topic.replace(' ', "-")))  # Check if CSV exists
    # Write to CSV file
    with open('static/staticData-{}.csv'.format(topic.replace(' ', "-")), 'a', newline='',
              encoding="utf-8-sig") as outputFile:
        writer = csv.DictWriter(outputFile, mined.keys())

        # Using dictionary keys as Column name for the CSV file if CSV doesn't exists
        if not csv_exsits:
            writer.writeheader()

        writer.writerow(mined)
    outputFile.close()


mysearch = f'{topic} -filter:retweets since:2021-08-15 until:2021-09-15 lang:"en" -filter:retweets -filter:links -filter:replies'
for i, tweet in enumerate(sntwitter.TwitterSearchScraper(mysearch).get_items()):
    if i > 4:  # 5 tweets
        break

    mined = {
        'tweet_id': tweet.id,
        'name': tweet.user.username,
        'retweet_count': tweet.retweetCount,
        'text': tweet.content,
        'created_at': tweet.date,
    }

    create_csv_files(mined)

# DONEEEEEEE
