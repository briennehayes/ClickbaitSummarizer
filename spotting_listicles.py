import pickle
df = pickle.load(open("cleaned_corpus.p", "rb"))

import spacy
nlp = spacy.load('en_core_web_sm')

def is_small_number(tok, thresh = 1000):
    """ Determines whether a token represents a "small" number (digit).

    Args:
        tok (spacy.tokens.token.Token): a spaCy token
        tresh (int): threshold for what should be considered "small"; default 1000

    Returns:
        bool: whether the token is a small number
    """
    if tok.is_digit:
        return int(tok.text) <= thresh
    return False

def get_lowered_tokens(doc):
    """ Outputs a list of lower-cased tokens in a document as strings.

    Args:
        doc (spacy.tokens.doc.Doc): a spaCy document

    Returns:
        list of strings: lower-cased tokens from the document
    """
    return [tok.lower_ for tok in doc]

def is_listicle(doc):
    """ Determines whether an article is a listicle based on its title.
    Obviously not perfect.

    Args:
        doc (spacy.tokens.doc.Doc): a spaCy document representing an article title

    Returns:
        bool: whether the document is a listicle
    """
    for sent in doc.sents:
        if is_small_number(sent[0]):
            ltoks = get_lowered_tokens(doc)
            flag_words = ["police", "dead", "shot", "killed", "injured"]
            try:
                if sent[1].lower_ != "minutes" and \
                    sent[1].lower_ != "percent" and \
                    sent[1].lower_ != "hours" and \
                    not sent[1].is_punct and \
                    not any([word in ltoks for word in flag_words]):
                    return True
            except IndexError:
                pass
    for i, tok in enumerate(doc):
        if tok.lower_ == "top" or tok.lower_ == "these" or tok.lower_ == "the":
            try:
                if is_small_number(doc[i + 1]):
                    return True
            except IndexError:
                pass
        elif tok.lower_ == "list" or tok.lower_ == "ranked":
            return True
        elif is_small_number(tok):
            try:
                if doc[i + 1].lower_ == 'things':
                    return True
            except IndexError:
                pass
    return False

def set_custom_boundaries(doc):
    """ Defines the colon as a sentence boundary.

    Args:
        doc (spacy.tokens.doc.Doc): a spaCy document

    Returns:
        spacy.tokens.doc.Doc: the spaCy document with updated sentence boundaries
    """
    for token in doc[:-1]:
        if token.text == ":":
            doc[token.i+1].is_sent_start = True
    return doc

nlp.remove_pipe('set_custom_boundaries')
nlp.add_pipe(set_custom_boundaries, before="parser")

def strip_the_list(title):
    """ Removes "The list" from the end of an article title

    Args:
        title (string): an article title

    Returns:
        string: the article title with "The list" removed from the end
    """
    if len(title) > 8:
        if title[-8:] == "The list":
            return title[:-8].strip()
    return title

# many article titles end with a reference to the site "The list" which throws off the listicle flagging rules
# fortunately, consistent formatting makes it easy to get rid of these
df['targetTitle'] = df['targetTitle'].apply(strip_the_list)

df['titleDoc'] = list(nlp.pipe(df['targetTitle']))

df['isListicle'] = df['titleDoc'].apply(is_listicle)

# check the distribution of listicles in the dataset
df.groupby(['isListicle', 'truthClass']).count()

# Extracting list items from listicles

# import re

# regex = "([0-9]+\..*?)"

# def text2int(textnum, numwords={}):
#     """ Retrieved from:
#     https://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers
#     """
#     if not numwords:
#       units = [
#         "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
#         "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
#         "sixteen", "seventeen", "eighteen", "nineteen",
#       ]

#       tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

#       scales = ["hundred", "thousand", "million", "billion", "trillion"]

#       numwords["and"] = (1, 0)
#       for idx, word in enumerate(units):    numwords[word] = (1, idx)
#       for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
#       for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

#     current = result = 0
#     for word in textnum.split():
#         if word not in numwords:
#           raise Exception("Illegal word: " + word)

#         scale, increment = numwords[word]
#         current = current * scale + increment
#         if scale > 100:
#             result += current
#             current = 0

#     return result + current