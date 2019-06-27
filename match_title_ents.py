import spacy
from spacy.tokens import Doc

def filter_spans(spans):
    """ Remove duplicate tokens from a list of spans.
        Adapted from code found here: https://spacy.io/usage/examples

    Args:
        spans (list of spacy.tokens.span.Span): the spans to be filtered, all from the same document

    Returns:
        list of spacy.tokens.span.Span: the list with duplicate tokens removed
    """
    # sort (in reverse) by span length, then by position in document
    get_sort_key = lambda span: (span.end - span.start, span.start)
    sorted_spans = sorted(spans, key = get_sort_key, reverse = True)
    result = []
    seen_tokens = set()
    for span in sorted_spans:
        if span.start not in seen_tokens and span.end - 1 not in seen_tokens:
            result.append(span)
            seen_tokens.update(range(span.start, span.end))
    # return spans in order found in document
    get_span_start = lambda span: span.start
    return sorted(result, key = get_span_start)

def retokenize_ents(doc):
    """ Retokenize a document by merging all tokens in noun chunks or named entities into single tokens.
        Also returns a dictionary mapping the indices of tokens in the original document to the index 
        of the token into which they were merged.
        Adapted from code found here: https://spacy.io/usage/examples
        
    Args:
        doc (spacy.tokens.doc.Doc): a spaCy document to be retokenized
        
    Returns:
        dict: mapping of indices of new tokens to indices of tokens that were merged
    """
    spans = list(doc.ents) + list(doc.noun_chunks)
    spans = filter_spans(spans) # removes spans that are both noun chunks and named ents
    mapping = {}
    subtract_length = 0 # offset from previous retokenized span
    with doc.retokenize() as retokenizer:
        for span in spans:
            ent_types = []
            for tok in span:
                mapping[tok.i] = span.start - subtract_length
                ent_types.append(tok.ent_type)
            # exact ent type doesn't matter, we just want to preserve whether any 
            # constituent tokens were originally named ents
            attrs = {"ENT_TYPE": max(ent_types)}
            subtract_length += len(span) - 1
            retokenizer.merge(span, attrs = attrs)
    return mapping

def match_title_ents(title, doc):
    """ Match ambiguous entities in an article title to named entities in the article.

    Args:
        title (spacy.tokens.doc.Doc): a spaCy document containing the title of the article
        doc (spacy.tokens.doc.Doc): a spaCy document containing the body of the article

    Returns:
        dict: keys are entities from the article title, values are lists of possible matches in the article body
    """ 
    doc_lemmas = [tok.lemma_.lower() for tok in doc] # look at lemmas since exact form of target root might not be used
    retok = Doc(doc.vocab).from_bytes(doc.to_bytes()) # don't want to overwrite tokenization of original document
    mapping = retokenize_ents(retok)
    matched = {}
    # want to try to locate an in-document match for each noun chunk, 
    # although we need some way to determine whether a chunk needs matching or not
    for chunk in title.noun_chunks:
        # print("THING WE'RE TRYING TO MATCH:", chunk)
        target_root = chunk.root # assumption: the root of the phrase should reoccur somewhere in doc
        # print("TARGET ROOT:", target_root)
        for sent in doc.sents:
            sent_lemmas = doc_lemmas[sent.start:sent.end]
            if target_root.lemma_ in sent_lemmas:
                # print("ROOT FOUND IN SENTENCE:", sent)
                # locate the retokenized token that contains the target root
                idx = doc_lemmas.index(target_root.lemma_, sent.start, sent.end)
                # I guess it's possible for target root to not be part of a noun chunk (somehow???)
                if idx in mapping:
                    pos = mapping[idx]
                    target_phrase = retok[pos]
                    match = None
                    # print("TARGET PHRASE:", target_phrase)
                else:
                    match = "?"
                while not match:
                    if target_phrase.ent_type:
                        match = target_phrase
                        # print("MATCH FOUND!:", match)
                        if chunk.text in matched:
                            matched[chunk.text].append(match.text)
                        else:
                            matched[chunk.text] = [match.text]
                    elif target_phrase.dep_ == "ROOT":
                        match = "?"
                        # print("MATCH NOT FOUND")
                    else:
                        target_phrase = target_phrase.head
        # what if the root isn't found?
        # IDEA: look for terms with high cosine similarity to the root/phrase
    return matched