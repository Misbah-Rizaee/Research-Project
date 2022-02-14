import json

import numpy
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("static/CSV/staticData-(afghanistan-afghan)-(refugee-refugees).csv")

# JSON FORMAT
sentAnalysis = json.loads(data.analysis.value_counts().to_json())
print(sentAnalysis)
# RETURNS 0 IF THE VALUE IS MISSING
print(sentAnalysis.get('Positive', 0))
print(sentAnalysis.get('Neutral', 0))
print(sentAnalysis.get('Negative', 0))


# PLOT IN A BAR CHART
def bar_chart():
    x = ['Positive', 'Neutral', 'Negative']
    h = [sentAnalysis.get('Positive', 0), sentAnalysis.get('Neutral', 0), sentAnalysis.get('Negative', 0)]
    c = [numpy.random.rand(3, ), numpy.random.rand(3, ), numpy.random.rand(3, )]

    plt.bar(x, h, align='center', color=c, alpha=0.5)
    plt.xlabel("Sentiment status")
    plt.ylabel('Number of Tweets')
    plt.title('Sentiment status of the tweets')
    plt.grid(axis='y')
    plt.savefig('static/Sentiment-Analysis.png')
    plt.show()


bar_chart()

# DONEEEE
