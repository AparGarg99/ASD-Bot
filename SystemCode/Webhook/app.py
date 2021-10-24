import pandas as pd
import json
from flask import Flask, Response, request, make_response, jsonify
import requests
import pandas as pd
from geopy.distance import geodesic
from opencage.geocoder import OpenCageGeocode
import flask_ngrok


app = Flask(__name__)
flask_ngrok.run_with_ngrok(app)

def mchatDiagnosis(req):
    invoke_next_question = True
    req = request.get_json(silent=True, force=True)
    #print(json.dumps(req, indent=4))   
    current_answer = req["queryResult"]["queryText"]
    current_question = req["queryResult"]["outputContexts"][0]["parameters"]["current-question"]
    if current_question[-2:].isdigit():
       current_question_number =  int(current_question[-2:])
       next_question = "question" + str(int(current_question[-2:]) + 1 )
    else:    
        next_question = "question" + str(int(current_question[-1:]) + 1 )
        current_question_number =  int(current_question[-1:])
    
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

    
    if current_question == "question20" :
        category = None
        if oCurrentScore < 3:
            category = "Low Risk"
            result = "Your childs Mchat score is " + str(oCurrentScore)+", your child is under " +category +" category therefore \
                    no further action required unless future monitoring indicates risk of ASD."
        if  oCurrentScore >= 3 and oCurrentScore<=7:
            category = "Medium Risk"
            result = "Your childs Mchat score is " + str(oCurrentScore) + ", your child is under "+ category +" category therefore \
                     ACTION recommended. Do refer your child for diagnostic evaluation and eligibility evaluation for early intervention."
        if  oCurrentScore >7:
            category = "High Risk"
            result = "Your childs Mchat score is " + str(oCurrentScore) + ", your child is under " + category + " category therefore ACTION required. Do refer immediately for diagnostic evaluation and eligibility evaluation for early intervention."
        
        
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
                                    },
                                    {
                                    "platform": "ACTIONS_ON_GOOGLE",
                                    "suggestions": {
                                        "suggestions": [
                                                       {
                                                       "title": "Acknowledged"
                                                       }
                                                       ]
                                                  }
                                    }
                                    ]
                    }
    else:
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
    # print ("reached here...")
    # res = json.dumps(bot_reply, indent=4)
    # # print(res)
    # r = make_response(res)
    # r.headers['Content-Type'] = 'application/json'
    # print("about to return")
    # return r
    return bot_reply

###############################################################################################

def get_coordinates(user_address):
    key = '59d9c102b504419f9c859fbe862dcfb5' # WeePing
    geocoder = OpenCageGeocode(key)
    results = geocoder.geocode(user_address)
    lat = results[0]['geometry']['lat']
    lon = results[0]['geometry']['lng']
    return (lat,lon)

###############################################################################################

def find_nearby(user_query,user_coor):
    d = {'Type': {0: 'Schools & Institutions', 1: 'Schools & Institutions', 2: 'Schools & Institutions', 3: 'Schools & Institutions', 4: 'Schools & Institutions', 5: 'Schools & Institutions', 6: 'Schools & Institutions', 7: 'Schools & Institutions', 8: 'Schools & Institutions', 9: 'Schools & Institutions', 10: 'Schools & Institutions', 11: 'Schools & Institutions', 12: 'Schools & Institutions', 13: 'Preschools', 14: 'Preschools', 15: 'Preschools', 16: 'Preschools', 17: 'Preschools', 18: 'Preschools', 19: 'Preschools', 20: 'Preschools', 21: 'Early Intervention Centers', 22: 'Early Intervention Centers', 23: 'Early Intervention Centers', 24: 'Early Intervention Centers', 25: 'Early Intervention Centers', 26: 'Early Intervention Centers', 27: 'Early Intervention Centers'}, 'Name': {0: 'Melbourne Specialist International School', 1: 'Integrated International School', 2: 'ABC Center Singapore', 3: 'Dover Court International School', 4: 'Eden School', 5: 'Metta School', 6: 'Pathlight School Campus 1', 7: 'Pathlight School Campus 2 (Main)', 8: 'Pathlight School Campus 2 (Annex)', 9: 'Singapore American School', 10: 'St. Andrew’s Autism School', 11: 'Towner Gardens School', 12: 'The Winstedt School', 13: 'Modern Montessori International Katong by The Growing Academy', 14: 'Bright Path Preschool', 15: 'Dyslexia Association of Singapore', 16: 'Genesis School for Special Education', 17: 'KidzRock International Preschool', 18: 'Mighty Oaks', 19: 'Nurture Pods', 20: 'Wee Care', 21: 'The Growing Academy', 22: 'All Hands Together', 23: 'Bridge Learning', 24: 'The Early Intervention Centre (EIC)', 25: 'Kaleidoscope', 26: 'KidsFirst', 27: 'Thumbs Up Therapy Singapore'}, 'Address': {0: '75C Loewen Rd, Singapore 248853', 1: '41 Sunset Way, #01-01, Singapore 597071', 2: '318 Tanglin Rd, Unit 01- 42 Phoenix Park Office Campus, Singapore 247979', 3: '301 Dover Rd, Singapore 139644', 4: '101 Bukit Batok West Ave 3, Singapore 659168', 5: '30 Simei Street 1, Singapore 529949', 6: '5 Ang Mo Kio Ave 10, Singapore 569739', 7: '6 Ang Mo Kio Street 44, Singapore 569253', 8: '2 Ang Mo Kio Street 44, Singapore 569250', 9: '40 Woodlands Street 41, Singapore 738547', 10: '1 Elliot Rd, Singapore 458686', 11: '1B Lengkong Lima, Singapore 417557', 12: '1208 Upper Boon Keng Rd, Singapore 387312', 13: '865 Mountbatten Road, #05-44, Singapore', 14: '55 Fairways Dr, Singapore 286846', 15: '1 Jurong West Central 2, #05-01 Jurong Point, Singapore', 16: '9 West Coast Rd, Singapore 127296', 17: '200 Turf Club Rd, 04-11, Singapore 287994', 18: '312A Tanglin Road 01-02 Phoenix Park Office Campus, Singapore 247982', 19: '314 Thomson Rd, Eng Aun Mansion, Singapore 307659', 20: '10 Winstedt Rd, #01-18 Block D, Singapore 227977', 21: '166 E Coast Rd, Singapore 428872', 22: '396 Joo Chiat Pl, Singapore 428079', 23: '20 Jurong West Street 93, #04-05 Sports & Recreation Centre, Singapore 648965', 24: '18 Ah Hood Rd, #06 - 52/54 Hiap Hoe Building, Singapore 329983', 25: '200 Turf Club Rd, 07-05/06, Singapore 287994', 26: '19 Tanglin Rd, Singapore 247909', 27: '24 Jln Kuning, Singapore 278169'}, 'coordinates': {0: '[1.3016393, 103.81243810000001]', 1: '[1.3235, 103.7675]', 2: '[1.3036, 103.8216]', 3: '[1.30552735, 103.77966431395433]', 4: '[1.3515, 103.743]', 5: '[1.3469, 103.9575]', 6: '[1.35937155, 103.85428306601094]', 7: '[1.3675032, 103.8580793]', 8: '[1.3640346499999998, 103.85839792650057]', 9: '[1.4258, 103.7755]', 10: '[1.3121317, 103.93163]', 11: '[1.3262, 103.9134]', 12: '[1.3167, 103.8736]', 13: '[1.30394, 103.901352]', 14: '[1.3406765, 103.7983864]', 15: '[1.33954, 103.70691]', 16: '[1.3177211, 103.7494615]', 17: '[1.33811, 103.7934]', 18: '[1.2984, 103.815]', 19: '[1.3235, 103.8421]', 20: '[1.31, 103.8418]', 21: '[1.3066, 103.9061]', 22: '[1.3149, 103.9102]', 23: '[1.3383, 103.6944]', 24: '[1.32731, 103.8466]', 25: '[1.3388, 103.7931]', 26: '[1.3062, 103.8266]', 27: '[1.3098, 103.7984]'}, 'lat': {0: 1.3016393, 1: 1.3235, 2: 1.3036, 3: 1.30552735, 4: 1.3515, 5: 1.3469, 6: 1.35937155, 7: 1.3675032, 8: 1.36403465, 9: 1.4258, 10: 1.3121317, 11: 1.3262, 12: 1.3167, 13: 1.30394, 14: 1.3406765, 15: 1.33954, 16: 1.3177211, 17: 1.33811, 18: 1.2984, 19: 1.3235, 20: 1.31, 21: 1.3066, 22: 1.3149, 23: 1.3383, 24: 1.32731, 25: 1.3388, 26: 1.3062, 27: 1.3098}, 'long': {0: 103.8124381, 1: 103.7675, 2: 103.8216, 3: 103.7796643139543, 4: 103.743, 5: 103.9575, 6: 103.8542830660109, 7: 103.8580793, 8: 103.8583979265006, 9: 103.7755, 10: 103.93163, 11: 103.9134, 12: 103.8736, 13: 103.901352, 14: 103.7983864, 15: 103.70691, 16: 103.7494615, 17: 103.7934, 18: 103.815, 19: 103.8421, 20: 103.8418, 21: 103.9061, 22: 103.9102, 23: 103.6944, 24: 103.8466, 25: 103.7931, 26: 103.8266, 27: 103.7984}}
    df=pd.DataFrame(d)
    df=df.loc[df['Type']==user_query]

    pt1 = user_coor

    l=[] 
    for i in range(df.shape[0]):
        lat2=df.iloc[i,-2]
        lng2=df.iloc[i,-1]
        pt2 = (lat2, lng2)
        l.append(round(geodesic(pt1, pt2).km,2))

    df['Distance(km)']= l
    df = df.sort_values(by=['Distance(km)']).reset_index(drop=True)

    text=''
    for i in range(3):
        if df.iloc[i,-1] < 50:
           text = text+df.iloc[i,1]+" ("+str(df.iloc[i,-1])+" km), "
        else:
           text = "I am sorry. I am unable to find coordinates for this address. Can you be more specific?" 

    
        #text = text+df.iloc[i,1]+" - "+str(df.iloc[i,-1])+"\n"

    return text

###############################################################################################

@app.route('/', methods=['POST'])
def main():

    req = request.get_json(silent=True, force=True)
    intent_name = req["queryResult"]["intent"]["displayName"]

    if(intent_name=='AnswerYes' or intent_name=='AnswerNo'):
       resp = mchatDiagnosis(req)


    elif(intent_name=='FindPlaces'):
        user_query = req["queryResult"]["queryText"]
        if(user_query=='Intervention Centers'):
            user_query='Early Intervention Centers'
        #print(user_query)
        user_address = req["queryResult"]["outputContexts"][0]["parameters"]["address"]

        user_coor = get_coordinates(user_address)

        try:          
          resp_text = find_nearby(user_query,user_coor)
        except:
          resp_text = "I am sorry. I am unable to find coordinates for this address. Can you be more specific?"

        #print("inside main func: ", resp_text)
    # else:
    #     resp_text = "Unable to find a matching intent. Try again."

        resp = {
            "fulfillmentMessages": [
                                    {
                                     "platform": "ACTIONS_ON_GOOGLE",
                                     "simpleResponses": {
                                         "simpleResponses": [
                                                            {
                                                             "textToSpeech": resp_text
                                                            }
                                                            ]
                                                         }                          
                                    },
                                                                        {
                                    "platform": "ACTIONS_ON_GOOGLE",
                                    "suggestions": {
                                        "suggestions": [
                                                       {
                                                       "title": "Noted"
                                                       }
                                                       ]
                                                  }
                                    }
                                    ]

    }

    return Response(json.dumps(resp), status=200, content_type="application/json")

if __name__ == '__main__':
    app.run()

# !pip install flask-ngrok
# !pip install opencage
# !pip install geopy

# !pip freeze > requirements.txt