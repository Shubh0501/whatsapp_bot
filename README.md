# whatsapp_bot

## Installation and Usage Steps

### Install python requirements

`pip3 -r requirements.txt`

### Setup the Database

* Run the commands in any PostgreSQL Database to create the respective tables which will be used to keep a track of whatsapp bot's usage
* All the commands that need to run can be found in create_database.sql file

### Run the backend

`python3 backend.py`

### Host the backend

There can be multiple ways to host the running backend into any cloud server such as AWS, to make it accessible to any system across, or You can use a platform "Ngrok" to make the backend server easily online, for development purposes.

For NGROK:
* Create an account on [Ngrok Platform](https://dashboard.ngrok.com)
* Once done, Download the ngrok package and follow the mentioned steps to install ngrok in your system
* Once the ngrok setup is completed, run the code to have ngrok forward your locally running backend through an open link
  ```ngrok http 5001```

* As you run this command, Ngrok dashboard in your terminal will show the values, where you will be able to see an SSL secured https link in "Forwarding" option. Save that link for future purposes

NOTE: Everytime you run ngrok, it will give you a new forwarding link, thus you will have to update the link in the next steps

### Setup Whatsapp Integration

* The project used the Whatsapp API provided by Twilio to enable users to interact with the system using Whatsapp
* In order to setup the API, create a new account in Twilio / use an already existing account
* Under "Messaging/Try it out" section, Go to "Send a Whatsapp Message" tab
* It provides you with an already existing Whatsapp Sandbox, which is running and can be interacted with
* From your personal whatsapp application, send the code mentioned in the sandbox, to the Mentioned number there in order to connect your number with the sandbox / You can directly scan the QR Code in the Sandbox
* Go to "Sandbox settings" from the top bar, and in the section of "When message comes in", paste the link that you get from Ngrok. Keep the method as "POST"
* Save the sandbox settings

### You are good to start interacting with the server now. You can start by sending a Hi Message in Whatsapp to start the Chatbot!
