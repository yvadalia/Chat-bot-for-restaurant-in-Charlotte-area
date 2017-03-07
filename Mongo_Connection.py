# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 14:29:45 2016

@author: yvadalia
"""
from pymongo import MongoClient
from nltk.parse.stanford import StanfordDependencyParser
from nltk.tag import StanfordNERTagger
import os

class MongoConnection:


    java_path = r"C:\Program Files (x86)\Java\jdk1.8.0_111\bin\java.exe"
    os.environ['JAVAHOME'] = java_path

    MONGO_CONNECTION_STRING = "mongodb://127.0.0.1:27017/"
    REVIEWS_DATABASE = "Dataset_Challenge"
    TAGS_DATABASE = "Tags"
    REVIEWS_COLLECTION = "Reviews"
    BUSINESS_COLLECTION = "Business"
    CORPUS_COLLECTION = "Corpus"
    
    reviews_collection = MongoClient(MONGO_CONNECTION_STRING)[REVIEWS_DATABASE][REVIEWS_COLLECTION]
    business_collection = MongoClient(MONGO_CONNECTION_STRING)[REVIEWS_DATABASE][BUSINESS_COLLECTION]
    
    path_to_jar =r'D:\Masters\Fall 2016\iNLP\Final Project\stanford-parser-full-2015-12-09\stanford-parser-full-2015-12-09\stanford-parser.jar'
    path_to_models_jar = r'D:\Masters\Fall 2016\iNLP\Final Project\stanford-parser-full-2015-12-09\stanford-parser-full-2015-12-09\stanford-english-corenlp-2016-10-31-models.jar'
    dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)
    
    st = StanfordNERTagger('D:\Masters\Fall 2016\iNLP\Final Project\stanford-ner-2015-12-09\stanford-ner-2015-12-09\classifiers\english.all.3class.distsim.crf.ser.gz',
                      'D:\Masters\Fall 2016\iNLP\Final Project\stanford-ner-2015-12-09\stanford-ner-2015-12-09\stanford-ner.jar') 