from twilio.twiml.messaging_response import MessagingResponse
import os
import psycopg2
import datetime
from dotenv import load_dotenv
from google.cloud.dialogflowcx_v3beta1.services.agents import AgentsClient
from google.cloud.dialogflowcx_v3beta1.services.sessions import SessionsClient
from google.cloud.dialogflowcx_v3beta1.types import session
from flask import Flask, request, jsonify

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
load_dotenv()
agent = f"projects/{os.getenv('PROJECT_ID')}/locations/{os.getenv('REGION_ID')}/agents/{os.getenv('AGENT_ID')}"

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
    return

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

    session_path = f"{agent}/sessions/{whatsappId}"
    client_options = None
    agent_components = AgentsClient.parse_agent_path(agent)
    location_id = agent_components['location']
    if location_id != "global":
        api_endpoint = f"{location_id}-dialogflow.googleapis.com:443"
        client_options = {"api_endpoint": api_endpoint}
    session_client = SessionsClient(client_options=client_options)
    text_input = session.TextInput(text=message)
    query_input = session.QueryInput(text=text_input, language_code='en-us')
    request1 = session.DetectIntentRequest(
        session=session_path, query_input=query_input
    )
    response = session_client.detect_intent(request=request1)

    print("=" * 20)
    print(f"Query text: {response.query_result.text}")
    response_messages = [
        " ".join(msg.text.text) for msg in response.query_result.response_messages
    ]
    print(f"Response text: {' '.join(response_messages)}\n")
    return sendMessage(str(''.join(response_messages)))

# Main Function to run the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)