from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from cytoolz import identity

def tokenize(doc):
    """ Simple tokenizer that removes punctuation and leaves tokens as lower-case.

    Args:
        doc (spacy.tokens.doc.Doc): spacy document to summarize tokenize

    Returns:
        list of strings: tokenizes representation of the document
    """
    return [tok.lower_ for tok in doc if not tok.is_punct]

def get_tfidf_matrix(docs):
    """ Builds a TFIDF matrix for a collection of documents.

    Args:
        docs (list of spacy.tokens.doc.Doc): corpus from which to construct TFIDF matrix.

    Returns:
        list of strings: all terms in the matrix, to be used for indexing
        sparse numpy array: the TFIDF matrix; rows represent documents, columns are terms
    """
    cv = CountVectorizer(analyzer = identity)
    tokens = [tokenize(doc) for doc in docs]
    counts = cv.fit_transform(tokens)
    tfidf = TfidfTransformer(norm = 'l2')
    weights = tfidf.fit_transform(counts)
    return cv.get_feature_names(), weights

def tfidf_summarizer(doc, doc_index, idx, tfidf, sum_length = 1):
    """ Summarize a document using TFIDF weighting. Requires a background corpus to build TFIDF matrix. 

    Args:
        doc (spacy.tokens.doc.Doc): document to summarize
        doc_index (int): which row in TFIDF matrix corresponds to this document
        idx (list of strings): first output from call to get_tfidf_matrix
        tfidf (sparse numpy array): second output from call to get_tfidf_matrix
        sum_length (int): number of sentences to extract for summary (default 1)

    Returns:
        string: document summary
    """
    
    weights = tfidf.copy()
    sents = list(doc.sents)

    sum_count = 0
    summary = []

    while sum_count < sum_length:

        best_sent = None
        best_weight = 0

        for sent in sents:
            if len(sent) >= 15:
                weight = 0
                for tok in sent:
                    if not tok.is_punct:
                        try:
                            weight += weights[doc_index, idx.index(tok.lower_)]
                        except ValueError:
                            pass
                weight = weight / len(sent)
                if weight > best_weight:
                    best_sent = sent
                    best_weight = weight
            
        summary.append(best_sent.text)
        sum_count += 1

        for tok in best_sent:
            if not tok.is_punct:
                weights[doc_index, idx.index(tok.lower_)] = weights[doc_index, idx.index(tok.lower_)] ** 2

    return " ".join(summary)