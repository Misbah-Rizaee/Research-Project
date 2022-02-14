import matplotlib.pyplot as plt
import nltk
import numpy
import pandas as pd
from gensim.models import Word2Vec
from nltk.corpus import stopwords

topic = 'war'

data = pd.read_csv("static/CSV/staticData-(afghanistan-afghan)-(refugee-refugees).csv")
# data = pd.read_csv("static/CSV/singleTopic-hello.csv")
text = [text.lower() for text in data["text"]]

sentences = [nltk.word_tokenize(sentence) for sentence in text]

for i in range(len(sentences)):
    sentences[i] = [word for word in sentences[i] if word not in stopwords.words('english')]

# Training the Word2Vec model
model = Word2Vec(sentences, min_count=1)

words = model.wv.index_to_key

# Finding Word Vectors
vector = model.wv[topic]

# Most similar words
similar = model.wv.most_similar(topic)
print(similar)


# PLOT IN THE GRAPH
keys = []
values = []
colours = []
for similarWord in similar:
    keys.append(similarWord[0])
    values.append(similarWord[1])
    colours.append(numpy.random.rand(3, ))

plt.bar(keys, values, align='center', color=colours, alpha=0.5)
plt.xlabel("Similar words")
plt.ylabel('Probability')
plt.title('Probability of other words that would appear with ({})'.format(topic), fontsize=10)
plt.grid(axis='y')
plt.xticks(rotation=90)
plt.savefig('static/Sentiment-Common-Words.png', bbox_inches='tight')
plt.show()

# DONEE
