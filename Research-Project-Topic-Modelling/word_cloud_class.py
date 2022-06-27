from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def preprocess_tweets(corpus):
    # Removing stopwords from the tweets
    stop_words = stopwords.words('english')
    stop_words.extend(['amp', 'even', 'maybe', 'another', 'getting', 'yet', 'lot', 'n\'t', 'seem', 'thing', 'anything'])
    processed_corpus = ""
    lemmatizer = WordNetLemmatizer()

    for document in corpus:
        word_list = [w for w in word_tokenize(document) if (w not in stop_words)]  # Remove stop words
        word_list = [lemmatizer.lemmatize(w) for w in word_list if len(w) > 2]  # lemmatized the words
        processed_corpus += " ".join(word_list) + " "

    return processed_corpus


def word_cloud():
    data = pd.read_csv("csv/old_tweets.csv")
    processed_corpus = preprocess_tweets(data['text'])

    # Creating the word cloud object
    wordcloud = WordCloud(width=1000, height=1000, margin=0, background_color='white',
                          colormap='tab10').generate(processed_corpus)

    plt.figure(figsize=(20, 20))  # Setting the size to 2000x2000
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.margins(x=0, y=0)
    plt.show()
