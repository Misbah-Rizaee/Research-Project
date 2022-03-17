import pandas as pd
import re
import nltk
import webbrowser, os

from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer, PorterStemmer

import gensim
from gensim import corpora
from gensim import models
import seaborn as sns
import matplotlib.pyplot as plt
import pyLDAvis.gensim_models

stopword = stopwords.words('english')


def preprocess_tweets(tweet):
    corpus = []
    stemmer = PorterStemmer()
    lem = WordNetLemmatizer()

    for tweets in tweet['text']:
        words = [w for w in word_tokenize(tweets) if (w not in stopword)]
        # words = [stemmer.stem(w) for w in word_tokenize(tweets) if (w not in stopword)]
        words = [lem.lemmatize(w) for w in words if len(w) > 2]
        corpus.append(words)

    return corpus


def save_topic_modeling(corpus):
    # Creating bag of words model using gensim
    dic = gensim.corpora.Dictionary(corpus)
    bow_corpus = [dic.doc2bow(doc) for doc in corpus]

    # Build LDA model
    lda_model = gensim.models.ldamodel.LdaModel(corpus=bow_corpus,
                                                id2word=dic,
                                                num_topics=10,
                                                random_state=10,
                                                update_every=1,
                                                chunksize=200,
                                                passes=5,
                                                alpha='auto',
                                                eval_every=1,
                                                iterations=100,
                                                per_word_topics=True)

    for idx, topic in lda_model.print_topics(-1):
        print('Topic: {} \nWords: {}'.format(idx, topic))

    # Visualize the topics
    vis = pyLDAvis.gensim_models.prepare(lda_model, bow_corpus, dic)
    pyLDAvis.save_html(vis, 'static/results/LDA-Topics.html')

    # OPEN IT DIRECTLY IN CHROME
    webbrowser.open('file://' + os.path.realpath("static/results/LDA-Topics.html"))

    # Plot
    fiz = plt.figure(figsize=(15, 30))
    for i in range(10):
        df = pd.DataFrame(lda_model.show_topic(i), columns=['term', 'prob']).set_index('term')
        #     df=df.sort_values('prob')

        plt.subplot(5, 2, i + 1)
        plt.title('topic ' + str(i + 1))
        sns.barplot(x='prob', y=df.index, data=df, label='Cities', palette='Reds_d')
        plt.xlabel('probability')

    plt.savefig('static/results/LDA-Topics.png')
    plt.show()


def start_analysing(data):
    # Removing stopwords from the tweets
    data['text'] = data['text'].astype(str).apply(lambda x: " ".join(x for x in x.split() if x not in stopword))
    corpus = preprocess_tweets(data)
    save_topic_modeling(corpus)


# DONEEE