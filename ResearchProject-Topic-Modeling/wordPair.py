from itertools import combinations
from collections import Counter

def collect_pairs(lines):
    pair_counter = Counter()
    for line in lines:
        unique_tokens = sorted(set(line))  # exclude duplicates in same line and sort to ensure one word is always before other
        combos = combinations(unique_tokens, 2)
        pair_counter += Counter(combos)
    return pair_counter