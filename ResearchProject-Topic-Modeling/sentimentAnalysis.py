import json
import pandas as pd
import matplotlib.pyplot as plt


data = pd.read_csv("static/CSV/singleTopic-hello.csv")

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
    c = ["blue", "grey", "green"]

    plt.bar(x, h, align='center', color=c)
    plt.xlabel("Sentiment")
    plt.ylabel('Number of Tweets')
    # plt.title('The data is based around ({})'.format(topic))

    # plt.savefig('static/staticData-{}.png'.format(topic))
    plt.show()


bar_chart()

# DONE
