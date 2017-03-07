# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 12:30:42 2016

@author: yvadalia
"""

import nltk
from nltk.corpus import stopwords
import string
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
import re


import gensim
from gensim import corpora, models

from nltk.tokenize import RegexpTokenizer


class ReviewQuestions:
    
    en_stop = stopwords.words('english')
    
    tokenizer = RegexpTokenizer(r'\w+')
    p_stemmer = LancasterStemmer()
    
    max_score = 0
    name_list = []
    location_list = []
    month_list = []
    time_list = []
    occupation_list = []
    location_prepo_list = []
    preposition_list = []
    numberInWords_list = []
    
    def semantic_classes(name_filename):
        with open(name_filename+"names.txt") as f:
            ReviewQuestions.name_list.append(f.read().splitlines())
    
        with open(name_filename+"location.txt") as f:
            ReviewQuestions.location_list.append(f.read().splitlines())
    
        with open(name_filename+"month.txt") as f:
            ReviewQuestions.month_list.append(f.read().lower().splitlines())
            
    
        with open(name_filename+"time.txt") as f:
            ReviewQuestions.time_list.append(f.read().lower().splitlines())
    
        with open(name_filename+"occupation.txt") as f:
            ReviewQuestions.occupation_list.append(f.read().lower().splitlines())
    
        with open(name_filename+"location_prepo.txt") as f:
            ReviewQuestions.location_prepo_list.append(f.read().lower().splitlines())
    
        with open(name_filename+"preposition.txt") as f:
            ReviewQuestions.preposition_list.append(f.read().lower().splitlines())
    
        with open(name_filename+"numberInWords.txt") as f:
            ReviewQuestions.numberInWords_list.append(f.read().lower().splitlines())
    
    input_path = "./"
    input_file = open(input_path+"testset1-inputfile.txt")
    input_data = input_file.read().splitlines()
    
    stopwordSet = stopwords.words('english')
    stopwordSet1 = set(['the','of','and','to','a','in','that','is','was','he','for','it','with','as','his','on','be','at','by','I'])
    morePunctuations = set(['``','"','...',"''","n't","'re","'s","--"])
    punctuationSet = set(string.punctuation) | morePunctuations
    porter_stemmer = PorterStemmer()
    
    
    def parse_review(name, review):
        review_dict = {}
        text = nltk.sent_tokenize(review.lstrip("\n").replace("\n"," "))
        review_dict[(name)] = text
        return review_dict
    
    def how_rule(sent,question,reviewPOS_dict):
    
        scoreOfHowRule = 0
        wordsInASentence = ReviewQuestions.wordTokenize(sent.lower())
        wordsInAQuestion = ReviewQuestions.wordTokenize(question.lower())
    
        #RULE 1
        scoreOfWordMatch = ReviewQuestions.wordMatch(question,sent,reviewPOS_dict)
        scoreOfHowRule = scoreOfHowRule + scoreOfWordMatch + 10
    
        #RULE 2
        if "cost" in wordsInAQuestion or "much" in wordsInAQuestion or "many" in wordsInAQuestion or "long" in wordsInAQuestion:
    
            if (("dollar" in wordsInASentence) or ("cost" in wordsInASentence) or (re.match(r'\d+',sent) != None) or ("weigh" in wordsInASentence)  ):
                scoreOfHowRule = scoreOfHowRule + 12
            for word in wordsInASentence:
                if word in ReviewQuestions.numberInWords_list:
                    scoreOfHowRule = scoreOfHowRule + 6
    
        #RULE 3
        if "age" in wordsInAQuestion or "old" in wordsInAQuestion:
            if (re.search(r'\d+',sent) != None):
                scoreOfHowRule = scoreOfHowRule + 20
            for word in wordsInASentence:
                if word in ReviewQuestions.numberInWords_list:
                    scoreOfHowRule = scoreOfHowRule + 20
    
        return scoreOfHowRule
    
    
    def why_rule(sent,BESTlines,text_list, index):
        wordsInASent = ReviewQuestions.wordTokenize(sent.lower())
        scoreOfWhyRule = 0
    
        if sent.lower() in BESTlines:
            scoreOfWhyRule = scoreOfWhyRule + 3
    
        if sent.lower() not in BESTlines:
            if (index + 1) < len(text_list):
                if text_list[index+1] in BESTlines:
                    scoreOfWhyRule = scoreOfWhyRule + 3
    
            if text_list[index - 1] in BESTlines:
                scoreOfWhyRule = scoreOfWhyRule + 4
    
        for word in wordsInASent:
            if word.lower() == "want":
                scoreOfWhyRule = scoreOfWhyRule + 4
            if ((word.lower() == "so") or (word.lower() == "because")) :
                scoreOfWhyRule = scoreOfWhyRule + 4
    
        return scoreOfWhyRule
    
    
    def what_rule(question,sent, scoreOfASentence):
        wordsInAQuestion = ReviewQuestions.wordTokenize(question)
        wordsInASentence = ReviewQuestions.wordTokenize(sent)
        scoreOfWhatRule = 0
    
        wordsAfterOfInAQues = []
    
        #RULE 1
        scoreOfWhatRule = scoreOfWhatRule + scoreOfASentence
    
        #RULE 2
        if (ReviewQuestions.contains_month(question) and ReviewQuestions.contains_relativetime(sent)):
            scoreOfWhatRule = scoreOfWhatRule + 3
    
        #RULE 3
        for ques_word in wordsInAQuestion:
            if ques_word == "kind":
                for sent_word in wordsInASentence:
                    if ((sent_word == "call" ) or (sent_word == "from")):
                        scoreOfWhatRule = scoreOfWhatRule + 4
    
        #RULE 4
        for ques_word in wordsInAQuestion:
            if ques_word == "name":
                for sent_word in wordsInASentence:
                    if ((sent_word == "name") or (sent_word == "call" ) or (sent_word == "known")):
                        scoreOfWhatRule = scoreOfWhatRule + 20
    
        for ques_word_index in range(len(wordsInAQuestion)):
            if wordsInAQuestion[ques_word_index] == "of":
                of_index = ques_word_index
                for remaining_word_index in range(of_index+1,len(wordsInAQuestion)):
                    wordsAfterOfInAQues.append(wordsInAQuestion[remaining_word_index].lower())
    
        #RULE 5
        for ques_word_index in range(len(wordsInAQuestion)):
            if wordsInAQuestion[ques_word_index] == "name":
                name_index = ques_word_index
                if wordsInAQuestion[name_index+1].lower() in ReviewQuestions.preposition_list[0]:
                    sentWithoutStopwords = ReviewQuestions.removeStopWords(sent)
                    if ReviewQuestions.contains_proper_noun(sentWithoutStopwords):
                        if ((ReviewQuestions.contains_proper_noun(sentWithoutStopwords)) and (ReviewQuestions.contains_head(wordsAfterOfInAQues,wordsInASentence))):
                            scoreOfWhatRule = scoreOfWhatRule + 20
    
        return scoreOfWhatRule
    
    
    def contains_head(wordsAfterOfInAQues,wordsInASentence):
        status = False
        wordsInASentenceLowercase = []
        for word in wordsInASentence:
            wordsInASentenceLowercase.append(word.lower())
    
        for word in wordsAfterOfInAQues:
            if word in wordsInASentenceLowercase:
                status = True
        return status
    
    def contains_month(question):
        wordsInAQuestion = ReviewQuestions.wordTokenize(question)
        status = False
        for word in wordsInAQuestion:
            if word.lower() in ReviewQuestions.month_list[0]:
                status = True
        return status
    
    def contains_relativetime(sent):
        wordsInASentence = ReviewQuestions.wordTokenize(sent)
        status = False
        for word in wordsInASentence:
            if ((word.lower() == "today") | (word.lower() == "yesterday")| (word.lower() == "tomorrow") | (word.lower() == "last night")):
                status = True
        return status
    
    def where_rule(question, sent, scoreOfASentence):
        score = 0
        score = score + scoreOfASentence
        if(ReviewQuestions.contains_location_prep(question, sent)):
            score = score + 4
        if(ReviewQuestions.contains_location_list(question, sent)):
            score = score + 6
    
        return score
    
    def contains_location_prep(sent, location_prepo_list):
        wordsInASent = nltk.word_tokenize(sent)
        sentWithoutPunct = []
        for word in wordsInASent:
            if word.lower() not in ReviewQuestions.punctuationSet:
                sentWithoutPunct.append(word)
    
        for word in sentWithoutPunct:
            if word in location_prepo_list[0]:
                status = True
            else:
                status = False
        return status
    
    def contains_location_list(sent, location_list):
        wordsInASent = nltk.word_tokenize(sent)
        sentWithoutPunct = []
        for word in wordsInASent:
            if word.lower() not in ReviewQuestions.punctuationSet:
                sentWithoutPunct.append(word)
    
        for word in sentWithoutPunct:
            if word in location_list[0]:
                status = True
            else:
                status = False
        return status
    
    def when_rule(question, sent, scoreOfASentence):
        score = 0
        score = score + scoreOfASentence
        if(ReviewQuestions.contains_time_list(sent, ReviewQuestions.time_list)):
            score = score + 4
    
        if(ReviewQuestions.contains_time_other(question, ["last"]) and ReviewQuestions.contains_time_other(sent,["first","last","since","ago"])):
            score = score + 20
        if(ReviewQuestions.contains_time_other(question, ["start","begin"]) and ReviewQuestions.contains_time_other(sent, ["start","begin","since","year"])):
            score = score + 20
    
        return score
    
    def contains_word(question,check):
        wordsInASent = nltk.word_tokenize(question)
        questionWithoutPunct = []
        for word in wordsInASent:
            if word.lower() not in ReviewQuestions.punctuationSet:
                questionWithoutPunct.append(word)
    
        if check in questionWithoutPunct:
            status = True
        else:
            status = False
        return status
    
    def dateline(question):
    
        score = 0
        if (ReviewQuestions.contains_word(question,"happen")):
            score =score + 4
        if (ReviewQuestions.contains_word(question,"take") and ReviewQuestions.contains_word(question,"place")):
            score =score + 4
        if (ReviewQuestions.ReviewQuestions.contains_word(question,"this")):
            score =score + 20
        if (ReviewQuestions.contains_word(question,"story")):
            score =score + 20
        return score
    
    
    def contains_time_other(sent, check_list):
        wordsInASent = nltk.word_tokenize(sent)
        sentWithoutPunct = []
        for word in wordsInASent:
            if word.lower() not in ReviewQuestions.punctuationSet:
                sentWithoutPunct.append(word)
    
        for word in sentWithoutPunct:
            if word in check_list:
                status = True
                return status
            else:
                status = False
        return status
    
    def contains_time_list(sent, time_list):
        wordsInASent = nltk.word_tokenize(sent)
        sentWithoutPunct = []
        for word in wordsInASent:
            if word.lower() not in ReviewQuestions.punctuationSet:
                sentWithoutPunct.append(word)
    
        for word in sentWithoutPunct:
            if word in time_list[0]:
                status = True
            else:
                status = False
        return status
    
    def who(questionWithoutStopWords, sentWithoutStopWords, reviewPOS_dict, scoreOfASentence):
        score = 0
        status = False
        score = score+ scoreOfASentence
        if(not ReviewQuestions.contains_noun(questionWithoutStopWords) and ReviewQuestions.contains_noun(sentWithoutStopWords)):
            score = score + 6
        if (not ReviewQuestions.contains_noun(questionWithoutStopWords) and ReviewQuestions.contains_name_word(sentWithoutStopWords)):
            score = score + 4
        status = ReviewQuestions.contains_name_occupation(sentWithoutStopWords)
        if (status):
            score = score + 4
        return score
    
    def contains_name_occupation(sentWithoutStopWord):
        proper_noun = ""
        status = False
        for word in sentWithoutStopWord:
            if (ReviewQuestions.camel(word)):
                proper_noun = proper_noun +" "+ word
    
        proper_noun_list = proper_noun.split()
    
        for each_proper_noun in proper_noun_list:
            if any(each_proper_noun in s for s in ReviewQuestions.name_list):
                status = True
                return status
    
        for word in sentWithoutStopWord:
            if any(word in s for s in ReviewQuestions.occupation_list):
                status = True
                return status
        return False
    
    def contains_noun(questionWithoutStopWord):
        status = False
        proper_noun = ""
        for word in questionWithoutStopWord:
            if (ReviewQuestions.camel(word)):
                proper_noun = proper_noun +" "+ word
    
        proper_noun_list = proper_noun.split()
        for each_proper_noun in proper_noun_list:
            if any(each_proper_noun in s for s in ReviewQuestions.name_list):
                status = True
                return status
        return status
    
    def contains_proper_noun(questionWithoutStopWord):
        status = False
        proper_noun = ""
        for word in questionWithoutStopWord:
            if (ReviewQuestions.camel(word)):
                status = True
        return True
    
    def contains_name_word(sentWithoutStopWords):
        status = False
        for word in sentWithoutStopWords:
            if (word == "name"):
                status = True
                return status
        return status
    
    def get_bestlines(question,text_list,reviewPOS_dict):
        scoreOfALine = {}
        BESTlines = []
    
        for line in text_list:
            scoreOfALine[line] = ReviewQuestions.wordMatch(question,line,reviewPOS_dict)
        print('\n')
        maxindex = max(scoreOfALine, key = scoreOfALine.get)
        maxScore = scoreOfALine[maxindex]
    #     print(maxindex+":"+str(maxScore))
    #     print('\n')
        #modify this to take average value
        twothirdMaxScore = 2/3.0*(maxScore)
        for line in scoreOfALine:
            if scoreOfALine[line] >= twothirdMaxScore:
                BESTlines.append(line.lower())
    
        return BESTlines
    
    def wordMatch(question, line, reviewPOS_dict):
        wordsInAQuestion = nltk.word_tokenize(question)
        rootsInAQuestion = set()
        for word in wordsInAQuestion:
            root = ReviewQuestions.porter_stemmer.stem(word)
            rootsInAQuestion.add(root)
    
        if line in reviewPOS_dict:
            verbmatch_score = 0
            rootmatch_score = 0
            scoreOfALine = {}
            for (word,tag) in reviewPOS_dict[line]:
                if 'V' in tag:
                    verb_root = ReviewQuestions.porter_stemmer.stem(word)
                    if verb_root in rootsInAQuestion:
                        verbmatch_score = verbmatch_score + 6
                else:
                    word_root = ReviewQuestions.porter_stemmer.stem(word)
                    if word_root in rootsInAQuestion:
                        rootmatch_score = rootmatch_score + 3
            scoreOfALine[line] = rootmatch_score + verbmatch_score
    #         print(scoreOfALine)
            return rootmatch_score + verbmatch_score
    
    
    def removeStopWords(line):
        wordsInALine = ReviewQuestions.wordTokenize(line)
        lineWithoutStopWords = []
        for word in wordsInALine:
            if word.lower() not in ReviewQuestions.stopwordSet:
                if word.lower() not in ReviewQuestions.punctuationSet:
                    lineWithoutStopWords.append(word)
        return lineWithoutStopWords
    
    
    def wordTokenize(line):
        wordsInALine = nltk.word_tokenize(line)
        return wordsInALine
    
    def removeStopWordsAndTagPOS(review_dict):
        reviewWithoutStopWords_dict = {}
        reviewPOS_dict = {}
        for key in review_dict:
            text = review_dict[key]
            for line in text:
                lineWithoutStopWord = ReviewQuestions.removeStopWords(line)
                reviewWithoutStopWords_dict[line] = lineWithoutStopWord
                reviewPOS_dict[line] = nltk.pos_tag(lineWithoutStopWord)
        return reviewWithoutStopWords_dict, reviewPOS_dict
    
    
    def camel(s):
        return (s != s.lower() and s != s.upper())
    
    def ldaTopics(ans):
        texts = []
        ans = list(nltk.word_tokenize(ans))
        for i in ans:
        # clean and tokenize document string
            raw = i.lower()
            tokens =ReviewQuestions. tokenizer.tokenize(raw)
        # remove stop words from tokens
            stopped_tokens = [i for i in tokens if not i in ReviewQuestions.en_stop]
        # stem tokens
            stemmed_tokens = [ReviewQuestions.p_stemmer.stem(i) for i in stopped_tokens]
        # add tokens to list
            texts.append(stopped_tokens)
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=5, id2word = dictionary, passes=20)
        topics = ldamodel.print_topics(num_topics=5, num_words=5)
        return topics
    
    def data_forward(question,review_dict):
        reviewWithoutStopWords_dict,reviewPOS_dict = ReviewQuestions.removeStopWordsAndTagPOS(review_dict)
        quest_words = set(['what','when','why','who','where','whose','which', 'how'])
        #for question in questions_data:
        for review_key in review_dict:
            text_list = review_dict[review_key]
            questionWithoutStopWords = ReviewQuestions.removeStopWords(question)
            BESTlines = ReviewQuestions.get_bestlines(question,text_list,reviewPOS_dict)
            
            
            for q in question.split():
                    if q.lower() in quest_words:
                        if q.lower() == 'who' or q.lower() == 'whose' :
                            max_score_who = 0
                            answer = ""
                            for sent in text_list:
                                scoreOfASentence = ReviewQuestions.wordMatch(question,sent,reviewPOS_dict)
                                sentWithoutStopWords = ReviewQuestions.removeStopWords(sent)
                                who_score = ReviewQuestions.who(questionWithoutStopWords,sentWithoutStopWords, reviewPOS_dict, scoreOfASentence)
    
                                if (max_score_who < who_score):
                                    max_score_who = who_score
                                    answer = sent
                            ans= ""
    
                            str1_list = nltk.word_tokenize(answer)
                            str2_list = nltk.word_tokenize(question.lower())
                            for word in str1_list:
                                if word.lower() not in str2_list and word.lower() not in ReviewQuestions.punctuationSet and not word.islower():
                                    ans = ans+" "+word
                            if ans == "":
                                for word in str1_list:
                                    if word.lower() not in str2_list and word.lower() not in ReviewQuestions.punctuationSet :
                                        ans = ans+" "+word
    
                            if 'being' in question and 'being' in ans:
                                ans = ans.split('being')[1]
                            topics = ReviewQuestions.ldaTopics(ans)
                            print("Question:",question)
                            print("Answer:", ans)
                            print("Topics:", topics)
                            break;
                            
                        if (q.lower() == 'when'):
                            max_score_when = 0
                            date = ""
                            count = 0
                            for sent in text_list:
                                scoreOfASentence = ReviewQuestions.wordMatch(question,sent,reviewPOS_dict)
                                when_score = ReviewQuestions.when_rule(question,sent, scoreOfASentence)
                                dateline_score = ReviewQuestions.dateline(question)
                                # dateline_score = 0
                                first_sent = text_list[0]
                                if (max_score_when < when_score):
                                    max_score_when = when_score
                                    answer = sent
    
                                if (when_score == max_score_when):
                                    count = count+1
    
                                if count == len(text_list):
                                    answer = first_sent
                                if  max_score_when == 0:
                                    max_score_when = dateline_score
                                    date = ReviewQuestions.story_key[1].split(":")[1].lstrip()
                                    answer = sent
                            date = ""
                            if date == "":
                                ans= ""
                                str1_list = nltk.word_tokenize(answer)
                                str2_list = nltk.word_tokenize(question.lower())
                                for word in str1_list:
                                    if word.lower() not in str2_list and word.lower() not in ReviewQuestions.punctuationSet:
                                        ans = ans+" "+word
    
                                if 'being' in question and 'being' in ans:
                                    ans = ans.split('being')[1]
    
                                print("Question:",question)
                                if (re.search(r'\d+',ans) != None):
                                    topics = ReviewQuestions.ldaTopics(re.sub('[^\d.]' , ' ', ans))
                                    print("Question:",question)
                                    print("Answer:", re.sub('[^\d.]' , ' ', ans))
                                    print("Topics:", topics)
                                else:
                                    topics = ReviewQuestions.ldaTopics(ans)
                                    print("Question:",question)
                                    print("Answer:", ans)
                                    print("Topics:", topics)
                            else:
                                ans= ""
                                str1_list = nltk.word_tokenize(answer)
                                str2_list = nltk.word_tokenize(question.lower())
                                for word in str1_list:
                                    if word.lower() not in str2_list and word.lower() not in ReviewQuestions.punctuationSet:
                                        ans = ans+" "+word
                                print( "Question:",question)
                                print( "Answer:", date)
                            break;
                        if(q.lower() == 'where'):
                            max_score_where = 0
                            date = ""
                            count =1
                            for sent in text_list:
                                scoreOfASentence = ReviewQuestions.wordMatch(question,sent,reviewPOS_dict)
                                where_score = ReviewQuestions.where_rule(question, sent, scoreOfASentence)
                                dateline_score = ReviewQuestions.dateline(question)
                                first_sent = text_list[0]
    
                                if (max_score_where < where_score):
                                    max_score_where = where_score
                                    answer = sent
    
                                if (where_score == max_score_where):
                                    count = count+1
    
                                if count == len(text_list):
                                    answer = first_sent
    
                                if max_score_where == 0:
                                    max_score_where = dateline_score
                                    date = ReviewQuestions.story_key[1].split(":")[1].lstrip()
                                    answer = sent
                                date = ""
    
                            if date == "":
                                ans= ""
                                str1_list = nltk.word_tokenize(answer)
                                str2_list = nltk.word_tokenize(question.lower())
                                for word in str1_list:
                                    if word.lower() not in str2_list and word.lower() not in ReviewQuestions.punctuationSet and not word.islower():
                                        ans = ans+" "+word
    
                                if 'being' in question and 'being' in ans:
                                    ans = ans.split('being')[1]
    
                                if ('where' in question) and 'from ' in ans:
                                    ans = ans[ans.index('from '):]
                                topics = ReviewQuestions.ldaTopics(ans)
                                print("Question:",question)
                                print("Answer:", ans)
                                print("Topics:", topics)
                            else:
                                ans= ""
                                str1_list = nltk.word_tokenize(answer)
                                str2_list = nltk.word_tokenize(question.lower())
                                for word in str1_list:
                                    if word.lower() not in str2_list and word.lower() not in ReviewQuestions.punctuationSet:
                                        ans = ans+" "+word
                                print( "Question:",question)
                                print( "Answer:", date)
                            break;
    
    
    
                        if(q.lower() == 'what' or q.lower() == 'which'):
                            max_score_what = 0
                            answer = ""
                            for sent in text_list:
                                scoreOfASentence = ReviewQuestions.wordMatch(question,sent,reviewPOS_dict)
                                scoreOfWhatRule = ReviewQuestions.what_rule(question, sent, scoreOfASentence)
    
                                if (scoreOfWhatRule == max_score_what):
                                    answer = answer + " | "+sent
    
                                if (max_score_what < scoreOfWhatRule):
                                    max_score_what = scoreOfWhatRule
                                    answer = sent
    
                            ans= ""
                            if "|" in answer:
                                str1_list = nltk.word_tokenize(answer.split("|")[1])
                            else:
                                str1_list = nltk.word_tokenize(answer)
                            str2_list = nltk.word_tokenize(question.lower())
                            for word in str1_list:
                                if word.lower() not in str2_list and word.lower() not in ReviewQuestions.punctuationSet:
                                    ans = ans+" "+word
    
                            if 'being' in question and 'being' in ans:
                                ans = ans.split('being')[1]
                            topics = ReviewQuestions.ldaTopics(ans)
                            print("Question:",question)
                            print("Answer:", ans)
                            print("Topics:", topics)
                            break;
    
                        if(q.lower() == 'why'):
                            index = -1
                            max_score_why = 0
                            answer = ""
                            for sent in text_list:
                                index = index + 1
                                scoreOfWhyRule = ReviewQuestions.why_rule(sent,BESTlines,text_list, index)
    
                                if (scoreOfWhyRule == max_score_why):
                                    answer = answer + " | "+sent
    
                                if (max_score_why < scoreOfWhyRule):
                                    max_score_why = scoreOfWhyRule
                                    answer = sent
    
                            ans= ""
                            str1_list = nltk.word_tokenize(answer)
                            str2_list = nltk.word_tokenize(question.lower())
    
                            if( "|" in answer ):
                                ans = answer.split("|")[-1]
                            else:
                                ans = answer
    
                            if 'being' in question and 'being' in ans:
                                ans = ans.split('being')[1]
                            if 'because' in ans:
                                ans = ans[ans.index('because '):]
    
                            elif 'for ' in ans:
                                ans = ans[ans.index('for '):]
    
                            elif 'to ' in ans:
                                ans = ans[ans.index('to '):]
                            topics = ReviewQuestions.ldaTopics(ans)
                            print("Question:",question)
                            print("Answer:", ans)
                            print("Topics:", topics)
                            break;
    
                        if(q.lower() == 'how'):
                            max_score_how = 0
                            for sent in text_list:
                                scoreOfHowRule = ReviewQuestions.how_rule(sent,question,reviewPOS_dict)
                                if (scoreOfHowRule == max_score_how):
                                    answer = answer + " | "+sent
    
                                if (scoreOfHowRule > max_score_how):
                                    max_score_how = scoreOfHowRule
                                    answer = sent
    
                            ans= ""
    
                            if ("|" in answer):
                                str1_list = nltk.word_tokenize(answer.split("|")[1])
                            else:
                                str1_list = nltk.word_tokenize(answer)
                            str2_list = nltk.word_tokenize(question.lower())
    
                            tagAnswer = nltk.pos_tag(str1_list)
                            if "how many" in question.lower() or "how much" in question.lower():
                                for i in range(0, len(tagAnswer)):
                                    if 'CD' in tagAnswer[i][1]:
                                        ans = ans + " " + tagAnswer[i][0]
                                    else:
                                        ans = answer
                            else:
                                for word in str1_list:
                                    if word.lower() not in str2_list and word.lower() not in ReviewQuestions.punctuationSet:
                                        ans = ans+" "+word
    
                            if 'being' in question and 'being' in ans:
                                ans = ans.split('being')[1]
    
                            if 'how' in question and 'by ' in ans:
                                ans = ans[ans.index('by '):]
    
                            if ('how' in question) and 'from ' in ans:
                                ans = ans[ans.index('from '):]
                            topics = ReviewQuestions.ldaTopics(ans)
                            print("Question:",question)
                            print("Answer:", ans)
                            print("Topics:", topics)
                            break;
    
    
            if not any(word in question.lower().split() for word in quest_words):
                    max_score_else = 0
                    answer = ""
                    for sent in text_list:
                        current_score = ReviewQuestions.wordMatch(question,sent,reviewPOS_dict)
    
                        if (current_score == max_score_else):
                                answer = answer + " | "+sent
    
                        if current_score > max_score_else:
                            max_score_else = current_score
                            answer = sent
    
                    ans= ""
                    if ("|" in answer):
                        str1_list = nltk.word_tokenize(answer.split("|")[1])
                    else:
                        str1_list = nltk.word_tokenize(answer)
                    str2_list = nltk.word_tokenize(question.lower())
                    for word in str1_list:
                        if word.lower() not in str2_list and word.lower() not in ReviewQuestions.punctuationSet:
                            ans = ans+" "+word
    
                    if 'being' in question and 'being' in ans:
                        ans = ans.split('being')[1]
                    topics = ReviewQuestions.ldaTopics(ans)
                    print("Question:",question)
                    print("Answer:", ans)
                    print("Topics:", topics)
            print("\n")
            
    
    def answerThis(question, review, name):
        review_dict = ReviewQuestions.parse_review(name, review)
        ReviewQuestions.semantic_classes("")
        ReviewQuestions.data_forward(question,review_dict)

