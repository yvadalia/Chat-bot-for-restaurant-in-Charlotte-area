# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 18:47:34 2016

@author: yvadalia
"""


import nltk
import string
import re

from collections import defaultdict

from Mongo_Connection import MongoConnection
from Review_Questions import ReviewQuestions

class BusinessQuestion:
    
    @staticmethod
    def getNN(text):
        text = nltk.word_tokenize(text)
        texttags = nltk.pos_tag(text)
        quesType = {}
        words = []
        for word,tag in texttags:
            if(tag == 'WDT'):
                quesType["type"] = "which"
            if(tag == 'WRB') and (word.lower()=='how'):
                quesType["type"] = "how"
            elif(tag == 'WRB') and (word.lower()=='where'):
                quesType["type"] = "where"                
            if(tag == 'WP'):
                quesType["type"] = "what"
            if(tag == 'NN' or tag == 'NNP'):
                words.append(word)
        quesType["words"] = words
        return quesType

    def getRestaurantName(question):
        restaurant_names = MongoConnection.business_collection.distinct("name")
        name_list = restaurant_names
        restaurant_names = [text.translate(str.maketrans('','',string.punctuation)) for text in restaurant_names]
        restaurant_name = [w for w in restaurant_names for words in question.lower().split() if w.lower() in words]
        if restaurant_name == []:
            ops = []
            count = 0
            for name in restaurant_names:
                ops.append(BusinessQuestion.restaurantName(name.lower().translate(str.maketrans('','',string.punctuation)), question.lower().translate(str.maketrans('','',string.punctuation))))
                if(name.lower() in ops):
                    return (name_list[count],restaurant_names)
                count = count+1
            return ("",restaurant_names)
        else:
            return (restaurant_name[0],restaurant_names)
            
    def restaurantName(s1, s2):
        m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
        (longest, x_longest) = (0, 0)
        for x in range(1, 1 + len(s1)):
            for y in range(1, 1 + len(s2)):
                if s1[x - 1] == s2[y - 1]:
                    m[x][y] = m[x - 1][y - 1] + 1
                    if m[x][y] > longest:
                        longest = m[x][y]
                        x_longest = x
                else:
                    m[x][y] = 0
        return s1[x_longest - longest:x_longest]

    def parseQuestion(question):
            result = MongoConnection.dependency_parser.raw_parse(question)
            output = {}
            for ret in result:
                temp = ret.root.get('deps')
                nsub = [value for key,value in temp.items() if key.startswith('nsubj')]
                if nsub:
                    subject = ret.get_by_address(nsub[0][0])
                    output["subject"] = subject.get('word')
                    nmod = subject.get('deps').get('nmod')
                    if nmod:
                        mod = ret.get_by_address(nmod[0])
                        output["nmod"] = mod.get('word')
        #                 print("NMOD :",mod.get('word'))
                        rel = mod.get('deps').get('acl:relcl')
                        if rel:
                            obj = ret.get_by_address(rel[0]).get('deps').get('dobj')
                            output["object"] = ret.get_by_address(obj[0]).get('word')
                        compound = mod.get('deps').get('compound')
                        if compound:
                            output["object"] = ret.get_by_address(compound[0]).get('word')
            return output
            
    def parseQuestionNltk(question):
        sent = nltk.pos_tag(nltk.word_tokenize(question))
        op = (nltk.ne_chunk(sent))
        result = {}
        for k, v in op.pos():
                result.setdefault(v, []).append(k[0])
        return result
        
    def parseQuestionStanford(question):
        op = MongoConnection.st.tag(question.split()) 
        result = {}
        for k, v in op:
                result.setdefault(v, []).append(k)
        return result
        
    def formQuery(question, quesType,restaurant_name,questionParsed,questionParsedNltk,questionParsedStanford):
            if restaurant_name != "":
                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})  
                output = []
#                Location check
                if(quesType["type"]== "where"):
                    if(("LOCATION" in questionParsedStanford) 
                    or ("LOCATION" in questionParsedNltk) 
                    or ("GPE" in questionParsedNltk)
                    or ("ORGANIZATION" in questionParsedNltk)
                    or ("ORGANIZATION" in questionParsedStanford)):
                        location = questionParsedStanford["LOCATION"] + questionParsedNltk["LOCATION"]+ questionParsedNltk["GPE"]+questionParsedNltk["ORGANIZATION"]
#                        print("Inside form query",location)
                        regexString = "|".join(location) 
#                        print("regexString",regexString)
                        address = [d["address"] for d in queryResult]
                        for text in address:
                            reResult = re.findall(regexString, text, re.IGNORECASE)
                            if(reResult!=[]):
                                output.append(text)
                        return output
                    else:
                       address = [d["address"] for d in queryResult]
                       return address
               
                elif(quesType["type"]=="what"):
                    if restaurant_name != "":
                        queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                        if(("LOCATION" in questionParsedStanford) 
                        or ("LOCATION" in questionParsedNltk) 
                        or ("ORGANIZATION" in questionParsedNltk)
                        or ("ORGANIZATION" in questionParsedStanford)):
                            location = questionParsedStanford["LOCATION"] + questionParsedNltk["LOCATION"]+ questionParsedNltk["GPE"]+questionParsedNltk["ORGANIZATION"]
                            regexString = "|".join(location) 
                            if("subject" in questionParsed):
                                subject = questionParsed["subject"]
                                if("rat" in subject) or ("star" in subject):
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    stars = [d['rating'] for d in queryResult]
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    address = [d["address"] for d in queryResult]
                                    starsOp = []
                                    for text in address:
                                        reResult = re.findall(regexString, text, re.IGNORECASE)
                                        if(reResult!=[]):
                                            output.append(text)
                                            starsOp.append(stars[address.index(text)])
                                    return dict(zip(output, starsOp))
                                elif("cost" in subject) or ("price" in subject):
                                    print("inside elif")
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    price = [d['price range'] for d in queryResult]
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    address = [d["address"] for d in queryResult]
                                    priceOp = []
                                    for text in address:
                                        reResult = re.findall(regexString, text, re.IGNORECASE)
                                        if(reResult!=[]):
                                            output.append(text)
                                            priceOp.append(price[address.index(text)])
                                    print((output, priceOp))
                                    return dict(zip(output, priceOp))
                            if("nmod" in questionParsed):
                                nmod = questionParsed["nmod"] 
                                if("rat" in nmod) or ("star" in nmod):
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    stars = [d['rating'] for d in queryResult]
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    address = [d["address"] for d in queryResult]
                                    starsOp = []
                                    for text in address:
                                        reResult = re.findall(regexString, text, re.IGNORECASE)
                                        if(reResult!=[]):
                                            output.append(text)
                                            starsOp.append(stars[address.index(text)])
                                    return dict(zip(output, starsOp))
                        else:
                            if("subject" in questionParsed):
                                print("Inside subject questionParsed")
                                subject = questionParsed["subject"]
                                if("rat" in subject) or ("star" in subject) or ("good" in subject):
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    stars = [d['rating'] for d in queryResult]
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    address = [d["address"] for d in queryResult]
                                    return dict(zip(address, stars))
                                elif("cost" in subject) or ("price" in subject):
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    price = [d['price range'] for d in queryResult]
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    address = [d["address"] for d in queryResult]
                                    print(dict(zip(address, price)))
                                    return dict(zip(address, price))
                            if("nmod" in questionParsed):
                                nmod = questionParsed["nmod"] 
                                if("rat" in nmod) or ("star" in nmod) or ("good" in nmod):
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    stars = [d['rating'] for d in queryResult]
                                    queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                    address = [d["address"] for d in queryResult]
                                    return dict(zip(address, stars))
                            words = quesType['words']
                            if("rate" in words) or ("rating" in words) or ("stars" in words) or ("rat" in words) or ("good" in words):
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                stars = [d['rating'] for d in queryResult]
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                address = [d["address"] for d in queryResult]
                                return dict(zip(address, stars))  
                            elif("address" in words) or ("location" in words):
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                address = [d["address"] for d in queryResult]
                                return address  
                            elif("parking" in words):
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                parking = [d['parking'] for d in queryResult if d['parking']!=""]
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                address = [d["address"] for d in queryResult]
                                return dict(zip(address, parking))    
                            elif("alcohol" in words) or ("beer" in words) or ("wine" in words) or ("bar" in words):
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                alcohol = [d['alcohol'] for d in queryResult if d['alcohol']!=""]
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                address = [d["address"] for d in queryResult]
                                return dict(zip(address, alcohol))    
                            elif("delivery" in words):
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                delivery = [d['delivery'] for d in queryResult if d['delivery']!=""]
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                address = [d["address"] for d in queryResult]
                                return dict(zip(address, delivery))    
                            elif("drive" in words) or ("thru" in words) or ("drive" in question.split()) or ("thru" in question.split()) or ("drive-thru" in question.split()):
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                driveThru = [d['drive thru'] for d in queryResult if d['drive thru']!=""]
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                address = [d["address"] for d in queryResult]
                                return dict(zip(address, driveThru))    
                            elif("cost" in words) or ("price" in words) or ("range" in question.split()) or ("cost" in question.split()) or ("price" in question.split()):
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                priceRange = [d['price range'] for d in queryResult if d['price range']!=""]
                                queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                                address = [d["address"] for d in queryResult]
                                return dict(zip(address, priceRange))
                else:
                    if restaurant_name != "":
                        words = quesType['words']
                        if("rate" in words) or ("rating" in words) or ("stars" in words) or ("rat" in words) or ("good" in words):
                            stars = [d['rating'] for d in queryResult]
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                            address = [d["address"] for d in queryResult]
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                            return dict(zip(address, stars))    
                        elif("parking" in words):
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                            parking = [d['parking'] for d in queryResult if d['parking']!=""]
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                            address = [d["address"] for d in queryResult]
                            return dict(zip(address, parking))    
                        elif("alcohol" in words) or ("beer" in words) or ("wine" in words) or ("bar" in words):
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                            alcohol = [d['alcohol'] for d in queryResult if d['alcohol']!=""]
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                            address = [d["address"] for d in queryResult]
                            return dict(zip(address, alcohol))    
                        elif("delivery" in words):
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                            delivery = [d['delivery'] for d in queryResult if d['delivery']!=""]
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                            address = [d["address"] for d in queryResult]
                            return dict(zip(address, delivery))    
                        elif("drive" in words) or ("thru" in words) or ("drive" in question.split()) or ("thru" in question.split()) or ("drive-thru" in question.split()):
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                            driveThru = [d['drive thru'] for d in queryResult if d['drive thru']!=""]
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                            address = [d["address"] for d in queryResult]
                            return dict(zip(address, driveThru))    
                        elif("cost" in words) or ("price" in words) or ("range" in question.split()) or ("cost" in question.split()) or ("price" in question.split()):
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})
                            priceRange = [d['price range'] for d in queryResult if d['price range']!=""]
                            queryResult = MongoConnection.business_collection.find({"name":restaurant_name})    
                            address = [d["address"] for d in queryResult]
                            return dict(zip(address, priceRange))    
#                            Write review code here
            elif restaurant_name == "":
                queryResult = MongoConnection.business_collection.find({})  
                output = []
                words = quesType['words']
                if("rate" in words) or ("rating" in words) or ("stars" in words) or ("rat" in words) or ("good" in words):
                    queryResult = MongoConnection.business_collection.find({})
                    stars = [d['rating'] for d in queryResult]
                    queryResult = MongoConnection.business_collection.find({})
                    address = [d["address"] for d in queryResult]
                    return dict(zip(address, stars))    
                elif("parking" in words):
                    queryResult = MongoConnection.business_collection.find({})
                    parking = [d['parking'] for d in queryResult if d['parking']!=""]
                    queryResult = MongoConnection.business_collection.find({})
                    address = [d["address"] for d in queryResult]
                    return dict(zip(address, parking))    
                elif("alcohol" in words) or ("beer" in words) or ("wine" in words) or ("bar" in words):
                    queryResult = MongoConnection.business_collection.find({})                      
                    alcohol = [d['alcohol'] for d in queryResult if d['alcohol']!=""]
                    queryResult = MongoConnection.business_collection.find({})
                    address = [d["address"] for d in queryResult]
                    return dict(zip(address, alcohol))    
                elif("delivery" in words):
                    queryResult = MongoConnection.business_collection.find({})
                    delivery = [d['delivery'] for d in queryResult if d['delivery']!=""]
                    queryResult = MongoConnection.business_collection.find({})
                    address = [d["address"] for d in queryResult]
                    return dict(zip(address, delivery))    
                elif("drive" in words) or ("thru" in words) or ("drive" in question.split()) or ("thru" in question.split()) or ("drive-thru" in question.split()):
                    queryResult = MongoConnection.business_collection.find({})
                    driveThru = [d['drive thru'] for d in queryResult if d['drive thru']!=""]
                    queryResult = MongoConnection.business_collection.find({})
                    address = [d["address"] for d in queryResult]
                    return dict(zip(address, driveThru))    
                elif("cost" in words) or ("price" in words) or ("range" in question.split()) or ("cost" in question.split()) or ("price" in question.split()):
                    queryResult = MongoConnection.business_collection.find({})
                    priceRange = [d['price range'] for d in queryResult if d['price range']!=""]
                    queryResult = MongoConnection.business_collection.find({})
                    address = [d["address"] for d in queryResult]
                    return dict(zip(address, priceRange))    
                else:
                    return ""
                
                

    @staticmethod
    def answerBusinessQuestion(question):
        quesType  = defaultdict(list,BusinessQuestion.getNN(question))
        restaurant_name, restaurant_names = BusinessQuestion.getRestaurantName(question)
        question_parsed = defaultdict(list,BusinessQuestion.parseQuestion(question))
        question_parsed_nltk = defaultdict(list, BusinessQuestion.parseQuestionNltk(question))
        question_parsed_stanford = defaultdict(list,BusinessQuestion.parseQuestionStanford(question))
        print(quesType,"\n", restaurant_name, "\n", question_parsed,"\n",question_parsed_nltk,"\n",question_parsed_stanford)
        result = BusinessQuestion.formQuery(question, quesType, restaurant_name, question_parsed,question_parsed_nltk,question_parsed_stanford)
        if(result==None) or (result==""):
            print("No relevant response in DB. Looking into reviews..!!")
            if(restaurant_name!=""):
                queryResult = MongoConnection.business_collection.find({"name": restaurant_name})  
                business_ids = []                
                reviews = []
                for d in queryResult:
                    business_ids.append(d['business_id'])
                    for i in range(len(business_ids)):
                        reviewsResult = MongoConnection.reviews_collection.find({"business":business_ids[i]})
                        for r in reviewsResult:
                            reviews.append(r['text'])
                totalReview = ' '.join(reviews)
                question = question.lower().translate(str.maketrans('','',string.punctuation)).replace(restaurant_name.lower().translate(str.maketrans('','',string.punctuation)),'')
                print("Question is :", question)
                ReviewQuestions.answerThis(question, totalReview, restaurant_name)
                return ""
            else:
#                reviewsResult = MongoConnection.reviews_collection.find({})
#                reviews = []
#                print("working1")
#                for r in reviewsResult:
#                    reviews.append(r['text'])
#                totalReview = ' '.join(reviews)
#                ReviewQuestions.answerThis(question, totalReview, "general")
                
                return "Please ask restaurant specific questions..!!"
        else:
            return result
        
        
        