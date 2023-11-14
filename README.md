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

FOR AWS:
* Create an account in AWS Console / Use an already existing AWS Account
* Search for EC2 in the searchbar, and Click on "Launch Instance"
* Give a name to the Instance, Select Linux as the environment and Launch the instance
* After a couple of minutes, the instance will be ready and in Running state
* Click on the instance ID and Click on "Connect" in the top bar
* In the SSH Client Tab, it provides you with the code that can be used to connect to the instance. Copy and paste the code in your local terminal to connect to the instance
* Using Git pull, import your codes in the instance storage, and install the libraries to run the server there
* Once you have the server running, you can access it by using the IPv4 address which is provided in the AWS Console - EC2 Instance Page
* AWS provides free SSL certificates, which you can use to make your server SSL secured OR You can use Ngrok in AWS instance to have an always running server in the instance
* If you use the SSL option from AWS, you will need your own domain and have to create Load balancers to redirect the traffic from the EC2 instance through your domain, in a secured manner. The SSL enabled link can then be used in the next steps

### Setup Whatsapp Integration

* The project used the Whatsapp API provided by Twilio to enable users to interact with the system using Whatsapp
* In order to setup the API, create a new account in Twilio / use an already existing account
* Under "Messaging/Try it out" section, Go to "Send a Whatsapp Message" tab
* It provides you with an already existing Whatsapp Sandbox, which is running and can be interacted with
* From your personal whatsapp application, send the code mentioned in the sandbox, to the Mentioned number there in order to connect your number with the sandbox / You can directly scan the QR Code in the Sandbox
* Go to "Sandbox settings" from the top bar, and in the section of "When message comes in", paste the link that you get from Ngrok. Keep the method as "POST"
* Save the sandbox settings

### You are good to start interacting with the server now. You can start by sending a Hi Message in Whatsapp to start the Chatbot!
