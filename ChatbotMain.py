# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 12:31:01 2016

@author: yvadalia
"""


from Business_Questions import BusinessQuestion

question = input("What do you want to know?  ")
bq = BusinessQuestion()
business_result = bq.answerBusinessQuestion(question)
print(business_result)


