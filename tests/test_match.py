""" Very simple demonstration of how match_title_ents works.
"""
from match_title_ents import match_title_ents
import spacy

nlp = spacy.load('en_core_web_sm')

with open("tests/test_data/title1.txt", "r") as text_file:
    title1 = nlp(text_file.read())

with open("tests/test_data/article1.txt", "r") as text_file:
    article1 = nlp(text_file.read())

with open("tests/test_data/title2.txt", "r") as text_file:
    title2 = nlp(text_file.read())

with open("tests/test_data/article2.txt", "r") as text_file:
    article2 = nlp(text_file.read())

print(match_title_ents(title1, article1))

print(match_title_ents(title2, article2))