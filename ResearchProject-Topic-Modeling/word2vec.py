import nltk
import pandas as pd
from gensim.models import Word2Vec
from nltk.corpus import stopwords
import re


data = pd.read_csv("static/CSV/singleTopic-hello.csv")
text = [text.lower() for text in data["text"]]
print(text)


sentences = [nltk.word_tokenize(sentence) for sentence in text]

for i in range(len(sentences)):
    sentences[i] = [word for word in sentences[i] if word not in stopwords.words('english')]

# Training the Word2Vec model
model = Word2Vec(sentences, min_count=1)

words = model.wv.index_to_key

# Finding Word Vectors
vector = model.wv['hello']

# Most similar words
similar = model.wv.most_similar('hello')
print(similar)

# DONE
