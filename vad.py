import spacy

nlp = spacy.load('en_core_web_lg')

import pandas as pd
import pickle

df = pickle.load(open("Data\clickbait.p", "rb"))
docs = pickle.load(open("Data/title_docs.p", "rb"))

df = df.merge(docs, left_index = True, right_index = True)

vad = pd.read_csv("Data/vad.csv", index_col = 1)
vad = vad[['V.Mean.Sum', 'A.Mean.Sum', 'D.Mean.Sum']]
vad = vad.rename(index = str, columns = {'V.Mean.Sum':'valence', 'A.Mean.Sum':'arousal', 'D.Mean.Sum':'dominance'})

import numpy as np
from collections import namedtuple

vadtup = namedtuple("vad", ['valence', 'arousal', 'dominance'])

def get_vad(doc):
    """ Returns the valence, arousal, and dominance scores for a document.
    """
    scores = [vadtup(vad.loc[tok.lemma_.lower()]['valence'], vad.loc[tok.lemma_.lower()]['arousal'], vad.loc[tok.lemma_.lower()]['dominance']) 
              for tok in doc if tok.lemma_.lower() in vad.index]
    
    avg_val = np.mean([tup.valence for tup in scores])
    avg_arous = np.mean([tup.arousal for tup in scores])
    avg_dom = np.mean([tup.dominance for tup in scores])
    
    return vadtup(avg_val, avg_arous, avg_dom)

vads = [get_vad(title) for title in df['titleDoc']]

df['valence'] = [v.valence for v in vads]
df['arousal'] = [v.arousal for v in vads]
df['dominance'] = [v.dominance for v in vads]

results = df[['valence', 'arousal', 'dominance']].copy()
results.to_csv("Results/vad_measures.csv")