import spacy
import operator
from collections import Counter

def sumbasic(doc, sum_length = 1):
    """ Implementation of sumbasic text summarization algorithm. Picks representative sentences based on high word frequencies.

    Args:
        doc (spacy.tokens.doc.Doc): spacy document to summarize
        sum_length (int): number of sentences for the summary

    Returns:
        string: document summary
    """
    tokens = [tok.norm_ for tok in doc if not tok.is_punct and not tok.is_stop]
    freqdist = Counter(tokens)
    probs = [freqdist[key] / len(tokens) for key in freqdist]
    probdict = dict(zip(freqdist.keys(), probs))
    sents = list(doc.sents)
    most_frequent_word = max(probdict.items(), key = operator.itemgetter(1))[0]

    sum_count = 0
    summary = []

    while sum_count < sum_length:

        best_sent = None
        best_weight = 0

        for sent in sents:
            weight = 0
            for tok in sent:
                if not tok.is_punct and not tok.is_stop:
                    weight += probdict[tok.norm_]
            weight = weight / len(sent)
            if weight > best_weight and most_frequent_word in sent.text.lower():
                best_sent = sent
                best_weight = weight
            
        summary.append(best_sent.text)
        sum_count += 1

        for tok in best_sent:
            if not tok.is_punct and not tok.is_stop:
                probdict[tok.norm_] = probdict[tok.norm_] ** 2

    return " ".join(summary)