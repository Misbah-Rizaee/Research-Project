from find_optimal_model import find_optimal_model
import pandas as pd

# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('omw-1.4')

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import gensim
from gensim import corpora
from gensim import models

import seaborn as sns
import matplotlib.pyplot as plt
import pyLDAvis.gensim_models


def preprocess_tweets(corpus):
    # Removing stopwords from the tweets
    stop_words = stopwords.words('english')
    stop_words.extend(['amp', 'even', 'maybe'])
    processed_corpus = []
    lemmatizer = WordNetLemmatizer()

    for document in corpus:
        word_list = [w for w in word_tokenize(document) if (w not in stop_words)]  # Remove stop words
        word_list = [lemmatizer.lemmatize(w) for w in word_list if len(w) > 2]  # lemmatized the words
        processed_corpus.append(word_list)

    return processed_corpus


def visualize_the_topics(lda_model, bow_corpus, dictionary):
    # Visualize the topics
    vis = pyLDAvis.gensim_models.prepare(lda_model, bow_corpus, dictionary)
    pyLDAvis.save_html(vis, 'result/topics.html')

    # Plot
    fiz = plt.figure(figsize=(15, 30))
    for i in range(4):
        df = pd.DataFrame(lda_model.show_topic(i), columns=['term', 'prob']).set_index('term')

        plt.subplot(5, 2, i + 1)
        plt.title('topic ' + str(i + 1))
        sns.barplot(x='prob', y=df.index, data=df, label='Cities', palette='Reds_d')
        plt.xlabel('probability')

    plt.savefig('result/topics.png')
    plt.show()


def topic_modelling():
    data = pd.read_csv("csv/old_tweets.csv")

    # file_names = ['csv/old_tweetsA.csv', 'csv/old_tweetsB.csv']
    # data = pd.concat((pd.read_csv(i, index_col=[0]) for i in file_names)).reset_index(drop=True)
    # data = data.sample(frac=1)  # Shuffle the rows

    processed_corpus = preprocess_tweets(data['text'])

    # Creating bag of words model using gensim
    dictionary = gensim.corpora.Dictionary(processed_corpus)
    bow_corpus = [dictionary.doc2bow(doc) for doc in processed_corpus]

    # Build LDA model
    lda_model = gensim.models.ldamodel.LdaModel(corpus=bow_corpus,
                                                id2word=dictionary,
                                                num_topics=5,
                                                random_state=200,  # WAS 10
                                                update_every=1,
                                                chunksize=200,
                                                passes=20,
                                                alpha='auto',
                                                eval_every=1,  # Setting this to one slows down training by ~2x
                                                iterations=100,
                                                per_word_topics=True)

    # visualize_the_topics(lda_model, bow_corpus, dictionary)

    find_optimal_model(lda_model, bow_corpus, processed_corpus, dictionary)



# DONEEE

