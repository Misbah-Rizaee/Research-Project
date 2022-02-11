from itertools import combinations
from collections import Counter
import pandas as pd
from nltk.corpus import stopwords

data = pd.read_csv("static/CSV/singleTopic-hello.csv")

stopword = stopwords.words('english')

filtered_words = []
for text in data['text']:
    singleText = text.split()
    list = []
    for singleWord in singleText:
        if singleWord not in stopword:
            list.append(singleWord)
    filtered_words.append(list)

print(filtered_words)


def collect_pairs(lines):
    pair_counter = Counter()
    for line in lines:
        unique_tokens = sorted(
            set(line))  # exclude duplicates in same line and sort to ensure one word is always before other
        combos = combinations(unique_tokens, 2)
        pair_counter += Counter(combos)
    return pair_counter


pairs = collect_pairs(filtered_words)
print(pairs.most_common(3))

# DONE
