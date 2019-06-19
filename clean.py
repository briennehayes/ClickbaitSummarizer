""" Read in clickbait corpus data, combine with truth labels, clean up text. 
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

# The clickbait corpus is German in origin, so some unicode irregularities need to be taken care of

import unicodedata
import re

def unicode_normalize(string):
    text = unicodedata.normalize("NFKD", string.replace("\xad", "")) # unlist the paragraphs and remove unicode
    text = re.sub(' +', ' ', text) # strip out any excess spaces
    return text

def clean_postText(post):
    return unicode_normalize("".join(post)) # mostly to unlist the single post text

def clean_keywords(kws):
    return [string.strip() for string in kws.split(",")]

def clean_paragraphs(ps):
    # paragraphs are given as lists of strings, so join them with newline character
    return unicode_normalize("\n".join(ps)) 

df['postText'] = df['postText'].apply(clean_postText)
df['targetKeywords'] = df['targetKeywords'].apply(clean_keywords)
df['targetParagraphs'] = df['targetParagraphs'].apply(clean_paragraphs)
df['targetTitle'] = df['targetTitle'].apply(unicode_normalize)

# many article titles end with a reference to the sitename "The list" 
# fortunately, consistent formatting makes it easy to get rid of these

def strip_the_list(title):
    if len(title) > 8:
        if title[-8:] == "The list":
            return title[:-8].strip()
    return title

df['targetTitle'] = df['targetTitle'].apply(strip_the_list)