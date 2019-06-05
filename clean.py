""" Read in clickbait corpus data, combine with truth labels, clean up text, and process with spaCy 
"""

import jsonlines as jl
import pandas as pd

with jl.open('instances.jsonl') as reader:
    df = pd.DataFrame()
    for obj in reader:
        df = df.append(obj, ignore_index = True)

df = df.set_index('id')
col_labels = ['truthJudgments', 'truthMean', 'truthMedian', 'truthMode', 'truthClass']
for label in col_labels:
    df[label] = None

with jl.open('truth.jsonl') as reader:
    for obj in reader:
        row_label = str(obj['id'])
        for label in col_labels:
            df.at[row_label, label] = obj[label]

import unicodedata
import re

def clean_postText(post):
    text = unicodedata.normalize("NFKD", "".join(post).replace("\xad", "")) # unlist the paragraphs and remove unicode
    text = re.sub(' +', ' ', text) # strip out any excess spaces
    return text

def clean_keywords(kws):
    return [string.strip() for string in kws.split(",")]

def clean_paragraphs(ps):
    text = unicodedata.normalize("NFKD", " ".join(ps).replace("\xad", "")) # unlist the paragraphs and remove unicode
    text = re.sub(' +', ' ', text) # strip out any excess spaces
    return text

def clean_titles(title):
    text = unicodedata.normalize("NFKD", title.replace("\xad", "")) # unlist the paragraphs and remove unicode
    text = re.sub(' +', ' ', text) # strip out any excess spaces
    return text

df['postText'] = df['postText'].apply(clean_postText)
df['targetKeywords'] = df['targetKeywords'].apply(clean_keywords)
df['targetParagraphs'] = df['targetParagraphs'].apply(clean_paragraphs)
df['targetTitle'] = df['targetTitle'].apply(clean_titles)

import spacy
nlp = spacy.load('en_core_web_sm')

df['postTextDoc'] = list(nlp.pipe(df['postText']))
df['paragraphsDoc'] = list(nlp.pipe(df['targetParagraphs']))