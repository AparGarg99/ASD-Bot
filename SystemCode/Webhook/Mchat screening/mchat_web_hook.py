# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 11:07:55 2021

@author: Gopan RG
"""

import json
import os

from flask import Flask
from flask import request
from flask import make_response

app = Flask(__name__)

@app.route('/', methods=['POST'])
def mchatDiagnosis():
    #get the request from dialogflow
    invoke_next_question = True
    req = request.get_json(silent=True, force=True)
    
    #fetch current question and answer
    current_answer = req["queryResult"]["queryText"]
    current_question = req["queryResult"]["outputContexts"][0]["parameters"]["current-question"]
    print("current_question - ", current_question)
    print("current_answer - ", current_answer)
    
    #get next question number
    if current_question[-2:].isdigit():
       current_question_number =  int(current_question[-2:])
       next_question = "question" + str(int(current_question[-2:]) + 1 )
    else:    
        next_question = "question" + str(int(current_question[-1:]) + 1 )
        current_question_number =  int(current_question[-1:])
    print ("next question - ", next_question)
    
    #calculating Score
    oCurrentScore = 0
    if current_question =="question1":
        oPreviousSCore = 0
    else:    
        oParameter = "parameter" +  str(current_question_number)
        oScoreParameter = req["queryResult"]["outputContexts"][0]["parameters"][oParameter]
        oPreviousScore = int(oScoreParameter.split(".")[1])
    oCurrentScore = oPreviousScore
        
    if (current_question_number not in [2,5,12]) and (current_answer == "No"):
        oCurrentScore = oCurrentScore + 1
    elif (current_question_number in [2,5,12]) and (current_answer == "Yes"):
        oCurrentScore = oCurrentScore + 1

    #trigger next question or send diagnosis result
    if current_question == "question20" :
        #send the final score and diagnosis result
        category = None
        if oCurrentScore < 3:
            category = "Low Risk"
            result = "Your childs Mchat score is " + str(oCurrentScore)+", your child is under " +category +" category therefore \
                    No further action required unless surveillance indicates risk for ASD"
        if  oCurrentScore >= 3 and oCurrentScore<=7:
            category = "Medium Risk"
            result = "Your childs Mchat score is " + str(oCurrentScore) + ", your child is under "+ category +" category therefore \
                     Action required: refer child for diagnostic evaluation and eligibility evaluation for early intervention"
        if  oCurrentScore >7:
            category = "High Risk"
            result = "Your childs Mchat score is " + str(oCurrentScore) + ", your child is under " + category + " category therefore Action required: refer immediately for diagnostic evaluation and eligibility evaluation for early intervention"
        
        
        bot_reply = {
            "fulfillmentMessages": [
                                    {
                                     "platform": "ACTIONS_ON_GOOGLE",
                                     "simpleResponses": {
                                         "simpleResponses": [
                                                            {
                                                             "textToSpeech": result
                                                            }
                                                            ]
                                                         }
                                     }
                                    ]
                    }
    else:
        #trigger next question
        bot_reply = {
            #user-answer is not used anywhere in the code but just showing you how to pass some values to the intent you are calling
            #https://dialogflow.com/docs/events
            "followupEventInput": {
                "name": next_question,
                "parameters": {
                    "user-answer": current_question + "." + str(oCurrentScore)
                    }
                }
            }  

    #send final response to dialogflow
    
    res = json.dumps(bot_reply, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    print("about to return")
    
    return r
    
   


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='localhost')