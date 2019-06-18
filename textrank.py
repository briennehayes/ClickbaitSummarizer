""" Implementation of TextRank algorithm for automated document summarization.

TextRank proposed by Mihalcea and Tarau (2004) in this paper:
https://www.aclweb.org/anthology/W04-3252

This code is adapted to work with spaCy from the TextRank summarizer contained in the sumy package:
https://pypi.org/project/sumy/
"""

import numpy as np
import math
from operator import itemgetter

delta = 1e-7 # prevents division by zero error when normalizing weight matrix
damping = 0.85 # probability of jumping to a connected vertex, following web surfer model
epsilon = 1e-4 # error tolerance for power method

def tokenize(doc):
    """ Split the tokens of a spaCy document into lemmas, removing punctuation and stopwords.

    Args:
        doc (spacy.tokens.doc.Doc): a spaCy document
    
    Returns:
        list of strings: the document's lemmatized tokens
    """
    return [tok.lemma_ for tok in doc if not tok.is_punct and not tok.is_stop]

def sent_similarity(sent1, sent2):
    """ Compute the similarity of two sentences, where similarity is based on the 
        number of tokens shared between the sentences.

        Takes sets of unique tokens as input to prevent repetitive sentences from being overrepresented.

        Args:
            sent1 (set of strings): the first sentence
            sent2 (set of strings): the second sentence sentence

        Returns:
            float: the similarity of the two argument sentences
    """
    sim = 0
    for tok1 in sent1:
        for tok2 in sent2:
            sim += int(tok1 == tok2)
            
    if sim == 0:
        return 0.0
    
    assert len(sent1) > 0 and len(sent2) > 0 # sentences must be non-empty
    norm = math.log(len(sent1)) + math.log(len(sent2))
    # prevents division-by-zero or division imprecision if either sentence is too short
    if np.isclose(norm, 0.):
        assert sim in (0, 1)
        return sim * 1.0
    else:
        return sim / norm

def get_edge_weights(doc):
    """ Compute the edge weights for the graph representation of the document.

    Args:
        doc (spacy.tokens.doc.Doc): a spaCy document

    Returns:
        numpy.array: the edge weights, with shape (# of sents in doc, # of sents in doc)
    """
    sents_tokens = [set(tokenize(sent)) for sent in doc.sents] # remove repeated words
    num_sents = len(list(doc.sents))
    weights = np.zeros((num_sents, num_sents))
    
    for i, sent_i in enumerate(sents_tokens):
        for j, sent_j in enumerate(sents_tokens):
            weights[i, j] = sent_similarity(sent_i, sent_j)

    weights /= (weights.sum(axis=1)[:, None] + delta)
    
    return np.full((num_sents, num_sents), (1. - damping) / num_sents) + damping * weights

def power_method(matrix, epsilon):
    """ Iterative power method for estimating largest eigenvalue and associated eigenvector of 
        a diagonalizable matrix. The eigenvector gives the TextRank sentence rankings.

        Args:
            matrix (numpy.array): a diagonalizable matrix
            epsilon (float): error tolerance for the estimation

        Returns:
            numpy.array: the estimated eigenvector
    """
    transposed_matrix = matrix.T
    num_sents = len(matrix)
    p_vector = np.array([1.0 / num_sents] * num_sents)
    lambda_val = 1.0

    while lambda_val > epsilon:
        next_p = np.dot(transposed_matrix, p_vector)
        lambda_val = np.linalg.norm(np.subtract(next_p, p_vector))
        p_vector = next_p

    return p_vector

def rate_sentences(doc):
    """ Generate TextRank rankings for all sentences in a document.

    Args:
        doc (spacy.tokens.doc.Doc): a spaCy document

    Returns:
        list of tuples: (sentence, ranking) for each sentence in the document
    """
    matrix = get_edge_weights(doc)
    ranks = power_method(matrix, epsilon)
    return [(sent.text, rank) for sent, rank in zip(doc.sents, ranks)]

def summarize(doc, num_sents):
    """ Produce a TextRank summary of a document.

    Args:
        doc (spacy.tokens.doc.Doc): a spaCy document
        num_sents (int): number of sentences to include in the summary

    Returns:
        string: the document summary
    """
    ranked_sents = rate_sentences(doc)
    sorted_sents = sorted(ranked_sents, key = itemgetter(1), reverse = True)
    return " ".join(sorted_sents[:num_sents])