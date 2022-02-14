import numpy
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("static/CSV/staticData-(afghanistan-afghan)-(refugee-refugees).csv", parse_dates=['created_at'])

# GET SUM OF RETWEETS
retweet_sum = data.groupby(pd.Grouper(key='analysis'))['retweet_count'].sum().dropna().reset_index()
retweet_sum.set_index("analysis", inplace=True)
# print(retweet_sum)

# PLOT THE ANALYSIS SCORE
x = ['Positive', 'Neutral', 'Negative']
h = [retweet_sum.loc['Positive']['retweet_count'], retweet_sum.loc['Neutral']['retweet_count'], retweet_sum.loc['Negative']['retweet_count']]
c = [numpy.random.rand(3, ), numpy.random.rand(3, ), numpy.random.rand(3, )]
plt.bar(x, h, align='center', color=c, alpha=0.5)
plt.xlabel("Sentiment status")
plt.ylabel('Sum of retweets')
plt.title('Sum of retweets per Sentiment status')
plt.grid(axis='y')
plt.savefig('static/Sentiment-Sum-Retweets.png', bbox_inches='tight')
plt.show()

# GET MEAN OF ANALYSIS SCORE
daily_mean = data.groupby(pd.Grouper(key='created_at', freq='W'))['analysis_score'].mean().dropna().reset_index()
# print(daily_mean)

# PLOT THE ANALYSIS SCORE
daily_mean.plot(x='created_at', y='analysis_score', kind='bar')
plt.xlabel("Weeks")
plt.ylabel('Weekly mean analysis score')
plt.title('Weekly mean of analysis scores')
plt.grid(axis='y')

import matplotlib.dates as mdates
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=3))

plt.savefig('static/Sentiment-Mean-Score.png', bbox_inches='tight')
plt.show()


# DONEE
