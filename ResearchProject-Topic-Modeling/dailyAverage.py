import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("static/CSV/singleTopic-hello.csv", parse_dates=['created_at'])

# GET SUM OF RETWEETS
retweet_sum = data.groupby(pd.Grouper(key='analysis'))['retweet_count'].sum().dropna().reset_index()
print(retweet_sum)

# GET MEAN OF ANALYSIS SCORE
daily_mean = data.groupby(pd.Grouper(key='created_at', freq='D'))['analysis_score'].mean().dropna().reset_index()
print(daily_mean)

# PLOT THE ANALYSIS SCORE
daily_mean.plot(x='created_at', y='analysis_score', kind='scatter')
plt.show()


# DONEE
