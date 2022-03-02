import spacy
import pandas as pd
import numpy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

list_ORG = []
list_PERSON = []
list_GPE = []
list_NORP = []
list_EVENT = []

# data = pd.read_csv("static/CSV/singleTopic-hello.csv")
data = pd.read_csv("static/CSV/staticData-(afghanistan-afghan)-(refugee-refugees).csv")

data.dropna(inplace=True)
# LIST OF LISTS
text = [text.lower() for text in data["text"]]

# SPLIT THE LISTS TO 10 PARTS
splited_list = numpy.array_split(text, 30)

for i in splited_list:
    # LIST OF TWEETS TO STRING SEPARATED BY DOT
    joined_text = ". ".join(i)

    nlp_text = nlp(joined_text)

    # FOR EACH WORD IN TEXT
    for entity in nlp_text.ents:
        if entity.label_ == "ORG":
            list_ORG.append(entity.text)
        if entity.label_ == "PERSON":
            list_PERSON.append(entity.text)
        if entity.label_ == "GPE":
            list_GPE.append(entity.text)
        if entity.label_ == "NORP":
            list_NORP.append(entity.text)
        if entity.label_ == "EVENT":
            list_EVENT.append(entity.text)

    # counter_ORG = Counter(list_ORG)
    # most_occur_ORG = dict(counter_ORG.most_common(10))
    # print(most_occur_ORG)
    #
    # counter_PERSON = Counter(list_PERSON)
    # most_occur_PERSON = dict(counter_PERSON.most_common(10))
    # print(most_occur_PERSON)
    #
    # counter_GPE = Counter(list_GPE)
    # most_occur_GPE = dict(counter_GPE.most_common(10))
    # print(most_occur_GPE)
    #
    # counter_NORP = Counter(list_NORP)
    # most_occur_NORP = dict(counter_NORP.most_common(10))
    # print(most_occur_NORP)
    #
    # counter_EVENT = Counter(list_EVENT)
    # most_occur_EVENT = dict(counter_EVENT.most_common(10))
    # print(most_occur_EVENT)


def send_data():
    # MOST OCCURRED WORDS
    counter_ORG = Counter(list_ORG)
    most_occur_ORG = dict(counter_ORG.most_common(10))

    counter_PERSON = Counter(list_PERSON)
    most_occur_PERSON = dict(counter_PERSON.most_common(10))

    counter_GPE = Counter(list_GPE)
    most_occur_GPE = dict(counter_GPE.most_common(10))

    counter_NORP = Counter(list_NORP)
    most_occur_NORP = dict(counter_NORP.most_common(10))

    counter_EVENT = Counter(list_EVENT)
    most_occur_EVENT = dict(counter_EVENT.most_common(10))

    return counter_ORG, counter_PERSON, counter_GPE, counter_NORP, counter_EVENT

# DONEE