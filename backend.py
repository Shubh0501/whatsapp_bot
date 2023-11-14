from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import os
import psycopg2
import datetime

# Array of Data to validate the input and responses. This can be added to a SQL Data table and fetched to make it dynamic in nature
greetingMessages = ['hi', 'hello', 'good morning', 'good afternoon', 'good evening', 'hey']
greetingOptions = [['eligibility for loan', 'eligibility', 'eligible'], ['faqs', 'faq']]
faqQuestions = ['What Loan products do you offer?', 'What is RevLoan?', 'What is your eligibility criteria?', 'How much can I borrow?', 'What will I need to apply for a loan?', 'How can I apply for a loan?', 'Where can I download your app?']
faqAnswers = ['We currently offer two types of loans to our customers, Personal Loan and RevLoan.', 'RevLoan is a unique revolving credit limit, which you can use and repay at any time per your convenience. With this limit, you will never need to apply for a small loan again!', 'We make lending decisions by taking into account the information provided by you in your application, the amount of credit you applied for, together with any additional information obtained from third party sources like credit bureaus.', 'How much you can borrow will depend on your individual needs and circumstances. We offer personal loans between Rs. 20,000 and Rs. 20,00,000. To check monthly repayments, you can use our EMI calculator.', 'You will need the following to apply for a loan:\na. Internet-enabled iOS or Android smartphone\nb. Your PAN and Aadhar card or any other address proof\nc. Your bank account details\nd. Your bank statements or internet banking login credentials', 'You can apply for a loan by downloading our iOS or Android applications.', 'You can download our iOS or Android application from  https://www.revfin.in.']
eligibilityQuestionIds = [
    {
        'id': 'age',
        'type': 'int',
        'correction_prompt': "Please enter your current age in number (from 1 to 100)",
        "question_prompt": 'Please enter your current age'
    },
    {
        'id': 'pincode',
        'type': 'int',
        'validation': {
            'length': 6
        },
        'correction_prompt': "Please enter your correct Pincode (Number having 6 digits)",
        "question_prompt": 'Please enter the pincode of your hometown'
    },
    {
        'id': 'occupation',
        'type': 'str_int',
        'validation': {
            'in': [{'str': 'salaried', 'int': '1'}, {'str': 'self employed', 'int': '2'}]
        },
        'correction_prompt': 'Please enter the correct response from one of the following:\n1 OR "Salaried"\n2 OR "Self Employed"',
        "question_prompt": 'What is your occupation?\nEnter 1 for Salaried\nEnter 2 for Self Employed'
    },
    {
        'id': 'type_of_loan',
        'type': 'str_int',
        'validation': {
            'in': [{'str': 'electric three wheeler loan', 'int': '1'}, {'str': 'electric two wheeler loan', 'int': '2'}, {'str': 'ev ancillary loan', 'int': '3'}]
        },
        'correction_prompt': 'Please enter the correct response from one of the following:\n1 or "ELectric Three Wheeler Loan"\n2 or "Electric Two Wheeler Loan"\n3 or "EV Ancillary Loan"',
        "question_prompt": 'Please select the type of loan your are looking for:\n 1 for Electric Three Wheeler Loan\n2 for Electric Two Wheeler Loan\n3 for EV Ancillary Loan'
    },
    {
        'id': 'salary',
        'type': 'int',
        'correction_prompt': 'Please enter your current salary in number',
        "question_prompt": 'What is your current income? (in Rupees)'
    },
    {
        'id': 'loan_amount',
        'type': 'int',
        'correction_prompt': "Please enter the amount of loan that you are seeking in number",
        "question_prompt": 'What is the amount of loan that you are looking for? (in Rupees)'
    },
    {
        'id': 'duration',
        'type': 'int',
        'correction_prompt': "Please enter the duration of the loan you are looking for in number (of months)",
        "question_prompt": 'What is the duration of the loan that you are looking for? (in Months)'
    }
]

# Initialising the App
app = Flask(__name__)

# Function which takes any string value and sends that as the response in Whatsapp
def sendMessage(value):
    bot_response = MessagingResponse()
    msg = bot_response.message()
    msg.body(value)
    return str(bot_response)

# Function to get a connection to the database
def getConnection():
    conn = None
    try:
        conn = psycopg2.connect(host="localhost", database="whatsapp_bot", user="postgres", port="5432")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        return conn

# Function to commit the changes and close the connection
def closeConnection(conn):
    conn.commit()
    conn.close()

# Function to get data from Database
def getDataFromDB(conn, query):
    val = None
    try:
        cur = conn.cursor()
        cur.execute(query)
        val = cur.fetchone()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        return val

# Function to add new data into database
def addDataToDB(conn, query):
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        return True

# Function to add new data into database
def addDataToDBWithReturn(conn, query):
    resp = None
    try:
        cur = conn.cursor()
        cur.execute(query)
        resp = cur.fetchone()[0]
        print("Returned Value: ", resp)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        return resp

# Function to update data in the database
def updateDataInDB(conn, query):
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        return ""

# Function to delete data from the database
def deleteDataFromDB(conn, query):
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        return ""

# Function to get the next message to be sent in order to check eligibility
def getNextMessage(conn, messages, data):
    resp = ""
    date_time = datetime.datetime.now()
    updateDataInDB(conn, "UPDATE active_sessions SET last_question_id='"+messages+"', update_time='"+str(date_time)+"' WHERE session_id='"+data[-2]+"'")
    for i in range(len(eligibilityQuestionIds)):
        if messages == eligibilityQuestionIds[i]['id']:
            resp = eligibilityQuestionIds[i]['question_prompt']
    if(resp == "" and messages=='verifyMessage'):
        addDataToDB(conn, "INSERT INTO verify_prompted VALUES('"+data[0]+"')")
        prevData = getDataFromDB(conn, "SELECT * FROM response_collection WHERE session_id='"+data[-2]+"'")
        resp = "We have got the following input from your side:\nAge: "+str(prevData[7])+"\nPincode: "+str(prevData[8])+"\nOccupation: "+prevData[9]+"\n Loan Type: "+prevData[10]+"\nCurrent Income: ₹"+prevData[11]+"\nLoan Amount: ₹"+prevData[12]+"\nLoan Duration: "+prevData[13]+" months\n\nPlease confirm the details by replying Yes."
    return resp

# Function to check if the user is eligible for loan or not
def getEligibility(values):
    age = int(values[7])
    amount = int(values[12])
    duration = int(values[13])
    if(age >= 21 and age <= 50 and amount >= 50000 and amount <= 150000 and duration >= 12 and duration <= 36):
        return "Eligible"
    else:
        return "Not Eligible"

# Function to check if the entered value is acceptable or not according to the validation logic
def checkIfValueIsAcceptable(value, eligibilityMap):
    type_of_data = eligibilityMap['type']
    typ_data_arr = str(type_of_data).split("_")
    if(len(typ_data_arr) == 1 and type_of_data=='int'):
        if(value.isdigit()):
            if('validation' not in eligibilityMap):
                return {'resp': True}
            elif(len(value) == eligibilityMap['validation']['length']):
                return {'resp': True}
            else:
                return {'resp': False}
        else:
            value_arr = str(value).split(" ")
            for i in value_arr:
                if(i.isdigit()):
                    if('validation' not in eligibilityMap):
                        return {'resp': True, 'correct': i}
                    elif(len(i) == eligibilityMap['validation']['length']):
                        return {'resp': True, 'correct': i}
            return {'resp': False}
    elif(len(typ_data_arr) == 2 and type_of_data=='str'):
        if('validation' not in eligibilityMap):
            return {'resp': True}
        elif(isinstance(value, str)):
            for i in eligibilityMap['validation']['in']:
                if(i in value):
                    return {'resp': True, 'correct': i}
            return {'resp': False}
        else:
            return {'resp': False}
    else:
        if('validation' not in eligibilityMap):
                return {'resp': True}
        elif(value.isdigit()):
            for i in eligibilityMap['validation']['in']:
                if(value == i['int']):
                    return {'resp': True, 'correct': i['str']}
            return {'resp': False}
        else:
            for i in eligibilityMap['validation']['in']:
                if(i['str'] in value):
                    return {'resp': True, 'correct': i['str']}
            value_arr = str(value).split(" ")
            for j in value_arr:
                if(j.isdigit()):
                    for i in eligibilityMap['validation']['in']:
                        if(j == i['int']):
                            return {'resp': True, 'correct': i['str']}
            return {'resp': False}

# Function which updates values in the response_collection table for the user
def updateUserResponses(conn, resp, sess_id, eligibilityMap):
    updateDataInDB(conn, "UPDATE response_collection SET "+eligibilityMap['id']+" = '"+resp+"' WHERE session_id='"+sess_id+"'")
    return

# Route to handle the response from Whatsapp
@app.route('/whatsapp_bot', methods=['POST'])
def whatsappBot():

    # Initialising input values START
    message = request.values.get('Body', '').lower()
    whatsappId = request.values.get('WaId', '910000000000').lower()
    fromStr = request.values.get('From', '').lower()
    account_name = request.values.get('ProfileName', '').lower()
    conn = getConnection()
    date_time = datetime.datetime.now()
    # Initialising input values END

    # Checking Previous Sessions START
    active_session = getDataFromDB(conn, "SELECT * FROM active_sessions WHERE whatsapp_id='"+whatsappId+"'")
    prev_message = None
    if(active_session):
        if(active_session[-2]):
            prev_message = getDataFromDB(conn, "SELECT * FROM response_collection WHERE session_id='"+active_session[-2]+"'")
        else:
            prev_message = getDataFromDB(conn, "SELECT * FROM response_collection WHERE whatsapp_id='"+whatsappId+"' AND final_decision IS NOT NULL ORDER BY end_time DESC")
    else:
        prev_message = getDataFromDB(conn, "SELECT * FROM response_collection WHERE whatsapp_id='"+whatsappId+"' AND final_decision IS NOT NULL ORDER BY end_time DESC")
        addDataToDB(conn, "INSERT INTO active_sessions (whatsapp_id, start_time, update_time) VALUES('"+whatsappId+"', '"+str(date_time)+"', '"+str(date_time)+"')")
    # Checking Previous Sessions END

    # If User sends a greeting Message START
    if(message in greetingMessages):
        # If they had previously tried, then sending the last eligibility check value
        if(prev_message):
            if(prev_message[-1]):
                return sendMessage('Hi,\n\nWelcome to Revfin. Your last eligibility check result was: *'+prev_message[-1]+'*.\n\nPlease select one from the following to start a new process:\n1. To check Eligibility for Loan, enter 1 or "Eligibility"\n2. To see FAQs, enter 2 or "FAQs"')
                
            elif(active_session):
                addDataToDB(conn, "INSERT INTO resume_prompted VALUES ('"+whatsappId+"')")
                return sendMessage('Hi,\n\nWelcome to Revfin. Do you want to resume your eligibility check process? Reply "Yes" to resume')
            else:
                return sendMessage('Hi,\n\nWelcome to Revfin. Please select the service you would like to avail today.\n1. To check Eligibility for Loan, enter 1 or "Eligibility"\n2. To see FAQs, enter 2 or "FAQs"')
        else:
            return sendMessage('Hi,\n\nWelcome to Revfin. Please select the service you would like to avail today.\n1. To check Eligibility for Loan, enter 1 or "Eligibility"\n2. To see FAQs, enter 2 or "FAQs"')
    # If User sends a greeting Message END

    # If user sends a confirmation Message START
    elif((message == 'yes' or message == 'yea' or message == 'y' or 'yes' in message.split(" ")) and (active_session and active_session[-1])):
        resume_exists = getDataFromDB(conn, "SELECT * FROM resume_prompted WHERE whatsapp_id='"+whatsappId+"'")
        verify_exists = getDataFromDB(conn, "SELECT * FROM verify_prompted WHERE whatsapp_id='"+whatsappId+"'")
        if(resume_exists):
            last_ques_id = active_session[-3]
            nextResp = getNextMessage(conn, last_ques_id, active_session)
            deleteDataFromDB(conn, "DELETE FROM resume_prompted WHERE whatsapp_id='"+whatsappId+"'")
            return sendMessage(nextResp)
        elif(verify_exists):
            nextResp = getEligibility(prev_message)
            sess_id = active_session[-2]
            date_time = datetime.datetime.now()
            updateDataInDB(conn, "UPDATE response_collection SET final_decision='"+nextResp+"', update_time= '"+str(date_time)+"', end_time= '"+str(date_time)+"' WHERE session_id='"+sess_id+"'")
            deleteDataFromDB(conn, "DELETE FROM verify_prompted WHERE whatsapp_id='"+whatsappId+"'")
            deleteDataFromDB(conn, "DELETE FROM active_sessions WHERE session_id='"+sess_id+"'")
            final_resp=""
            if(nextResp=='Eligible'):
                final_resp = "*Congratulations!!!🥳🥳🥳*\n\nYou are eligible for a loan from us. Kindly visit https://www.revfin.in to get in touch with us and start your journey with Revfin! 🤝"
            else:
                final_resp = "We are really sorry, but there's no available offers for your account yet!😔\n\nBut don't lose hope, visit https://www.revfin.in to learn how you can improve your chances of getting a loan and start your journey with Revfin! 👍\n\n\nReply with 'Hi' to start a new process"
            return sendMessage(final_resp)
        else:
            if(active_session):
                last_ques_id = active_session[-3]
                resp = ""
                for i in len(range(eligibilityQuestionIds)):
                    if(last_ques_id == eligibilityQuestionIds[i]['id']):
                        resp = eligibilityQuestionIds[i]['correction_prompt']
                if(not resp):
                    resp = 'I am sorry, but I am unable to understand the message. Please select one of the following:\n1. To check Eligibility for Loan, enter 1 or "Eligibility"\n2. To see FAQs, enter 2 or "FAQs"'
                return sendMessage(resp)
            else:
                return sendMessage('I am sorry, but I am unable to understand the message. Please select one of the following:\n1. To check Eligibility for Loan, enter 1 or "Eligibility"\n2. To see FAQs, enter 2 or "FAQs"')
    # If user sends a confirmation Message END

    # If the user sends a Denying message START
    elif ((message == 'no' or message == 'n' or 'no' in message.split(" ")) and (active_session and active_session[-1])):
        resume_exists = getDataFromDB(conn, "SELECT * FROM resume_prompted WHERE whatsapp_id='"+whatsappId+"'")
        verify_exists = getDataFromDB(conn, "SELECT * FROM verify_prompted WHERE whatsapp_id='"+whatsappId+"'")
        if(resume_exists or verify_exists):
            deleteDataFromDB(conn, "DELETE FROM resume_prompted WHERE whatsapp_id='"+whatsappId+"'")
            deleteDataFromDB(conn, "DELETE FROM verify_prompted WHERE whatsapp_id='"+whatsappId+"'")
            deleteDataFromDB(conn, "DELETE FROM active_sessions WHERE whatsapp_id='"+whatsappId+"'")
            return sendMessage("No problem! Send 'Hi' to start a new journey!")
        else:
            last_ques_id = active_session[-3]
            resp = ""
            for i in range(len(eligibilityQuestionIds)):
                if(last_ques_id == eligibilityQuestionIds[i]['id']):
                    resp = eligibilityQuestionIds[i]['correction_prompt']
            if(not resp or resp == ""):
                resp = 'I am sorry, but I am unable to understand the message. Please select one of the following:\n1. To check Eligibility for Loan, enter 1 or "Eligibility"\n2. To see FAQs, enter 2 or "FAQs"'
            return sendMessage(resp)
    # If the user sends a Denying message START

    # If user wants to check eligibility START
    elif(message in greetingOptions[0] or ('eligible' in message) or ('eligibility' in message) or (active_session and not active_session[-1] and message == str(1))):
        # Complete process for the user
        print("HEREEEE")
        updateDataInDB(conn, "UPDATE active_sessions SET session_type='eligibility' WHERE whatsapp_id='"+whatsappId+"'")
        date_time = datetime.datetime.now()
        sess_id = addDataToDBWithReturn(conn, "INSERT INTO response_collection(whatsapp_id, from_account, account_name, start_time, update_time) VALUES('"+whatsappId+"', '"+fromStr+"', '"+account_name+"', '"+str(date_time)+"', '"+str(date_time)+"') RETURNING session_id;")
        print("Session id: ", sess_id)
        updateDataInDB(conn, "UPDATE active_sessions SET session_id = '"+sess_id+"' WHERE whatsapp_id='"+whatsappId+"'")
        active_session = getDataFromDB(conn, "SELECT * FROM active_sessions WHERE session_id='"+sess_id+"'")
        question = getNextMessage(conn, eligibilityQuestionIds[0]['id'], active_session)
        return sendMessage(question)
    # If user wants to check eligibility END

    # If user wants to see FAQs START
    elif(message in greetingOptions[1] or 'question' in message or 'doubt' in message or (active_session and not active_session[-1] and message == str(2))):
        # Send list of FAQs to the user
        updateDataInDB(conn, "UPDATE active_sessions SET session_type='faqs' WHERE whatsapp_id='"+whatsappId+"'")
        print("Data Updated")
        return sendMessage('What would you like to know today?\n1. '+faqQuestions[0]+'\n2. '+faqQuestions[1]+'\n3. '+faqQuestions[2]+'\n4. '+faqQuestions[3]+'\n5. '+faqQuestions[4]+'\n6. '+faqQuestions[5]+'\n7. '+faqQuestions[6])
    # If user wants to see FAQs END

    # If user wants to see a FAQ Answer START
    elif((active_session and active_session[-1] == 'faqs')):
        for i in range(len(faqQuestions)):
            if(message == faqQuestions[i].lower() or message == faqQuestions[i][:-1].lower() or message == str(i+1) or str(i+1) in message):
                return sendMessage(faqAnswers[i])
        return sendMessage('This is not a valid FAQ Question. Please select one from the following:\n\n1. '+faqQuestions[0]+'\n2. '+faqQuestions[1]+'\n3. '+faqQuestions[2]+'\n4. '+faqQuestions[3]+'\n5. '+faqQuestions[4]+'\n6. '+faqQuestions[5]+'\n7. '+faqQuestions[6]+'\n\n Or Enter "Eligibility" to check your eligibility for loan')
    # If user wants to see a FAQ Answer END

    # If user wants inputs any other value START
    else:
        if(not active_session or (active_session and not active_session[-1])):
            resp = 'I am sorry, but I am unable to understand the message. Please select one of the following:\n1. To check Eligibility for Loan, enter 1 or "Eligibility"\n2. To see FAQs, enter 2 or "FAQs"'
            return sendMessage(resp)
        else:
            last_ques = active_session[-3]
            for i in range(len(eligibilityQuestionIds)):
                if(last_ques == eligibilityQuestionIds[i]['id']):
                    validInput = checkIfValueIsAcceptable(message, eligibilityQuestionIds[i])
                    if(not validInput['resp']):
                        resp = eligibilityQuestionIds[i]['correction_prompt']
                        return sendMessage(resp)
                    else:
                        c_message = message
                        if('correct' in validInput):
                            c_message = validInput['correct']
                        nextId = None
                        if(i < len(eligibilityQuestionIds)-1):
                            nextId = eligibilityQuestionIds[i+1]['id']
                        else:
                            nextId = "verifyMessage"
                        updateUserResponses(conn, c_message, active_session[-2], eligibilityQuestionIds[i])
                        nextQues = getNextMessage(conn, nextId, active_session)
                        return sendMessage(nextQues)
    # If user wants inputs any other value END
    return 'I am sorry, but I am unable to understand the message. Please select one of the following:\n1. To check Eligibility for Loan, enter 1 or "Eligibility"\n2. To see FAQs, enter 2 or "FAQs"'
    
# Main Function to run the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)