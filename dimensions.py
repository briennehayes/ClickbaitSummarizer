import re
import spacy
import pickle
import pandas as pd
from listicles import is_listicle
from textblob import TextBlob
from pattern.en import parse, Sentence, parse
from pattern.en import modality

# Word Lists
you_forms = ["you", "your", "yours"]
question_words = ["who", "what", "where", "when", "why", "how"]
flag_words = ["police", "dead", "shot", "killed", "injured"] # these are words that tend to throw off the listicle identifier
irr_superlatives = ["best", "worst", "furthest", "farthest", "least", "most"]

# Dimension Measure Functions
def leads_with_question(doc):
    """ Indicates whether a title leads with a question word.
    """
    return doc[0].text.lower() in question_words

def has_det(doc):
    """ Indicates whether any noun phrases in the title contain a determiner.
    """
    return any([tok.pos_ == "DET" for chunk in doc.noun_chunks for tok in chunk])

def accusatory(doc):
    """ Indicates whether the title refers directly to the reader.
    """
    return any([tok.text.lower() in you_forms for tok in doc])

def pattern_parse(text):
    """ Parses a text into a pattern Sentence object.
    """
    s = parse(text, lemmata = True)
    s = Sentence(s)
    return s

def is_superlative(tok):
    """ Indicates whether a token is a superlative.
    """
    text = tok.text.lower()
    if text in irr_superlatives:
        return True
    elif re.search("est$", text):
        return text[:-3] == tok.lemma_
    return False

def has_superlative(doc):
    """ Indicates whether a title contains a superlative.
    """
    return any([is_superlative(tok) for tok in doc])

# Data load
df = pickle.load(open("clickbait.p", "rb"))
docs = pickle.load(open("title_docs.p", "rb"))
df = df.merge(docs, left_index = True, right_index = True)

# Run analysis
df['polarity'] = df['titleBlob'].apply(lambda blob: blob.sentiment.polarity)
df['subjectivity'] = df['titleBlob'].apply(lambda blob: blob.sentiment.subjectivity)
df['pattern'] = df['targetTitle'].apply(pattern_parse) # THIS WILL SOMETIMES FAIL FOR NO REASON. If you keep re-running it, it eventually works.
df['modality'] = df['pattern'].apply(lambda s: modality(s))
df['listicle'] = df['titleDoc'].apply(is_listicle)
df['leadsWithQuestion'] = df['titleDoc'].apply(leads_with_question)
df['hasDeterminer'] = df['titleDoc'].apply(has_det)
df['numNamedEntities'] = df['titleDoc'].apply(lambda doc: len(doc.ents))
df['superlative'] = df['titleDoc'].apply(has_superlative)
df['accusatory'] = df['titleDoc'].apply(accusatory)

# Data export
stats = df[['truthMean', 'truthMedian', 'truthMode', 'truthClass', 
            'polarity', 'subjectivity', 'modality', 'listicle', 
            'leadsWithQuestion', 'hasDeterminer', 'numNamedEntities', 'superlative', 
            'accusatory']].copy()

stats['listicle'] = stats['listicle'].astype('int')
stats['leadsWithQuestion'] = stats['leadsWithQuestion'].astype('int')
stats['hasDeterminer'] = stats['hasDeterminer'].astype('int')
stats['superlative'] = stats['superlative'].astype('int')
stats['accusatory'] = stats['accusatory'].astype('int')

stats.to_csv("dim_stats.csv")