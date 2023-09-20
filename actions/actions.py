# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.events import FollowupAction
from rasa_sdk.events import Restarted
import smtplib
import os
import openai
import requests
from dotenv import load_dotenv

#This instantiates the prompt we want the bot to follow
messageBase= [{"role": "system", "content": "You are a helpful assistant."},]

# Runs if bot does not understand user's input
class ActionDefaultAskAffirmation(Action):

   def name(self):
       return "action_default_ask_affirmation"

   async def run(self, dispatcher, tracker, domain):
       print("in ActionDefaultAskAffirmation!!!")
	
       # Last thing user typed
       ##lastOutput = tracker.latest_message['text']
       # Gets the user's last intent by extracting it from tracker dict
       # lastUserIntentDictionary = tracker.latest_message['intent']
       
       #lastUserIntent = list(lastUserIntentDictionary.values())[1]
       #print("Last USER intent: " + lastUserIntent)
       #lastBotQuestion = tracker.latest_action_name
       #print(lastBotQuestion)
        
       # Gets last output of bot (last question that bot asked user)
       ##for event in tracker.events:
           ##if (event.get("event") == "bot"):
               ##lastBotMessage = event.get("text")
       ##print(lastBotMessage)
       
       # email fallback
       ##if "Please type the name of the person you want to email." in lastBotMessage:
           ##dispatcher.utter_message('The person you want to email is ' + lastOutput)
           ##SlotSet("recipient", lastOutput)
           ##return [FollowupAction("collect_email_info")]
       ##elif "Please enter the email address of the person you want to email." in lastBotMessage:
           ##dispatcher.utter_message('The email address is ' + lastOutput)
           ##SlotSet("email", lastOutput)
           ##return [FollowupAction("collect_email_info")]
       ##else:
           ##dispatcher.utter_message(text="すみません、わかりません。 Sorry, I don't quite understand (,,>﹏<,,).", image = "https://media.tenor.com/-caxkmc867EAAAAC/mochi-cat.gif")
       return [FollowupAction("call_chatgpt")]

# Followup action from ActionDefaultAskAffirmation that
# generates the bot's next response 

# I don't think we need this       
class AfterHandleDidNotUnderstandAnswer(Action):

    def name(self) -> Text:
        return "after_handle_did_not_understand_answer"

    def run(self, dispatcher, tracker, domain):
        print("in AfterHandleDidNotUnderstandAnswer")

        # Gets last output of bot (based on dispatcher.utter_message from ActionDefaultAskAffirmation)
        for event in tracker.events:
            if (event.get("event") == "bot"):
                lastBotMessage = event.get("text")
        print(lastBotMessage)

        # Gets the user's last intent by extracting it from tracker dict
        lastUserIntentDictionary = tracker.latest_message['intent']
        lastUserIntent = list(lastUserIntentDictionary.values())[0]

	# Asks user for to ask bot a question
        # The lastBotMessage is coming from the ActionDefaultAskAffirmation
        # and these if/elif statements are checking what the bot last said
        # and using substrings of the last message to identify what the bot says next
        
        # Fallback for if the bot doesn't understand the receipient's name for the email or the email address
        if "The person you want to email is" in lastBotMessage:
            dispatcher.utter_message('Great. Now we need their email.')
        elif "The email address is" in lastBotMessage:
            dispatcher.utter_message('Thank you for the information.')
        # else
        else:
            return [FollowupAction("call_chatgpt")]
        
        print(lastUserIntent)
        return [Restarted()]

#Create action to log conversation, each time called will capture last bot output
class LogConversationBot(Action):
  
    def name(self) -> Text:
         # Name of the action
        return "log_conversation_bot"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
	
	# Get last conversation for bot
        print("In log conversation bot")  
        for event in tracker.events:
            if (event.get("event") == "bot"):
                lastBotMessage = "Bot message: " + event.get("text")

        print("Last bot message: " + lastBotMessage)

        # Creates/Open function to open the file "conversation_[senderID].txt" 
        # with the senderID being unique to each user
        uniqueFile = "conversationLogs/conversation_" + tracker.sender_id + ".txt"
        conversation_txt = open(uniqueFile,"a")


        conversation_log_bot = "\n" + lastBotMessage 
        
        # write latest conversations to txt file
        conversation_txt.write(conversation_log_bot)

        conversation_txt.close()

#Create action to log conversation, each time called will capture last user response
class LogConversationUser(Action):
  
    def name(self) -> Text:
         # Name of the action
        return "log_conversation_user"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
	
        # print last user message
        print("In log conversation user")    
        print("Last user message: " + tracker.latest_message.get("text"))


        # Creates/Open function to open the file "conversation_[senderID].txt" 
        # with the senderID being unique to each user
        uniqueFile = "conversationLogs/conversation_" + tracker.sender_id + ".txt"
        conversation_txt = open(uniqueFile,"a")

        # Get last conversation from user
        conversation_log_user = tracker.latest_message.get("text")
        
        # write latest conversations to txt file
        conversation_txt.write("\nUser message: " + conversation_log_user)
        conversation_txt.close()         


# Action to create text file with information to send email
class CollectEmailInfo(Action):
  
   def name(self) -> Text:
        # Name of the action
       return "collect_email_info"
  
   def run(self, dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

       # Get last conversation from user
       print("In Collect email inform") 
       conversation_log_user = tracker.latest_message.get("text")

       # Extracting user name, recipient of email name, and email address
       # Gets the user's last intent by extracting it from tracker dict
       lastUserIntentDictionary = tracker.latest_message['intent']
       lastUserIntent = list(lastUserIntentDictionary.values())[0]
       print("Last user intent when running CollectEmailInfo: " + str(lastUserIntent))

       if "inform_recipient" in lastUserIntent:
           emailFile = "emailInfo/emailInfo_" + tracker.sender_id + ".txt"
           email_txt = open(emailFile,"a")
           email_txt.write(conversation_log_user +"\n")
           print("recipient recorded in text file")   
       elif "inform_email" in lastUserIntent:
           print("intent is inform email")
           emailFile = "emailInfo/emailInfo_" + tracker.sender_id + ".txt"
           email_txt = open(emailFile,"a")
           words = conversation_log_user.split()
           for word in words:
               if "@" in word:
                   email_txt.write(word + "\n")
           print("email recorded in text file")

       email_txt.close()
       


# Creating new class to send emails.
class ActionEmail(Action):
  
    def name(self) -> Text:
         # Name of the action
        return "action_email"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Tracker message log
        # message_log = tracker.latest_message['text']
        # conversation_log = str(tracker.get_slot("conversation_log"))        

        # Getting the data stored in the
        # slots and storing them in variables.
        # these are for the person RECIEVING the mail
        print("In action_email") 
        emailFile = "conversationLogs/conversation_" + tracker.sender_id + ".txt"
        email_txt = open(emailFile,"r") 

        name = tracker.get_slot("name")
        recipient = "Professor"
        email_address = tracker.get_slot("choose_professor_email_slot")
        print("email address slot is " + email_address)
 
        email_txt.close()        
        
        # recipient = tracker.get_slot("recipient")
        # email_address = tracker.get_slot("email")
        # name = tracker.get_slot("name")
        # recipient = "Leah"
        # email_address = "bryantt@dickinson.edu"
          
        # Code to send email
        # Creating connection using smtplib module
        s = smtplib.SMTP('localhost')
          
        # Making connection secured
        s.starttls() 
         
        # Authentication
        # s.login("goldberl@dickinson.edu")

        
        # Open the file "conversation_[senderID].txt" 
        # with the senderID being unique to each user
        uniqueFile = "conversationLogs/conversation_" + tracker.sender_id + ".txt"
        conversation_txt = open(uniqueFile,"r")

        conversation_log = ''
        # Using for loop
        for line in conversation_txt:
            conversation_log = conversation_log + line +'\n'
    
        # Closing files
        conversation_txt.close()
          
        # Message to be sent
        # Ideally we would like to say who this conversation is from which can be extracted 
        # from the NAME slot if the bot did not delete all the slots
        # But the bot sometimes deletes all the slots
        # One way we can fix this is storing the user's name in a text file and reading it
        # Additionally, to ensure the bot understands the email address, we can put that in a 
        # txt file as well and read it
        message = "Subject: Japanese Chatbot Message Log\n\n Hello {} \n\nThis is a message from the RASA Japanese chatbot!\n\nRegards,\nThe Dickinson College RASA Japanese Chatbot".format(recipient) + "\n\nPlease find the message log below for the conversation: \n" + conversation_log
        
	# The email address below is the person who is SENDING the mail  
        # Sending the mail
        s.sendmail("academictechnology@dickinson.edu",email_address, message.encode("utf8"))
        # Closing the connection
        s.quit()

        # Delete contents of conversation_[senderID].txt
        uniqueFile = "conversationLogs/conversation_" + tracker.sender_id + ".txt"
        if os.path.exists(uniqueFile):
            os.remove(uniqueFile)
            # Confirmation message
            dispatcher.utter_message(text="Email has been sent.")
        
        emailFile = "conversationLogs/conversation_" + tracker.sender_id + ".txt"
        if os.path.exists(emailFile):
            os.remove(emailFile)          

        return []
       

# Creating new class to send emails.
class DeleteConversationTxt(Action):
  
    def name(self) -> Text:
         # Name of the action
        return "action_delete_conversation_txt"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Delete contents of conversation.txt
        print("In delete conversations txt") 
        uniqueFile = "conversationLogs/conversation_" + tracker.sender_id + ".txt"
        uniqueFileTwo = "conversationLogs/questionCounter_" + tracker.sender_id + ".txt"
        if os.path.exists(uniqueFile):
            os.remove(uniqueFile)
        if os.path.exists(uniqueFileTwo):
            os.remove(uniqueFileTwo)
        return []
        

class ActionMakeFile(Action):
# this custom action makes it so that we initialize a file to write to for counting questions
    def name(self) -> Text:
        return "action_make_file"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
	domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
	
        print("In action_make_file")        
        uniqueFile = "conversationLogs/questionCounter_" + tracker.sender_id + ".txt"
        #conversation_txt = open(uniqueFile,"r") Refrence code to help with formatting
       	question_txt = open(uniqueFile, "w")
        question_txt.write("0")
        question_txt.close()


#class ActionDummmy(Action):

#    def name(self) -> Text:
#        return "action_dummy"

#    def run(self, dispatcher: CollectingDispatcher,
#        tracker: Tracker,
#        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#        print("HELLO this is a dummy action that restarts the conversation.")
#        return[Restarted()]

class CallChatGPT(Action):

    def name(self) -> Text:
        return "call_chatgpt"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        load_dotenv()
        #Do we want to put something here where we check if user said yes to send email, if so record conversation?
        #Alternative is to track regardless then ask them at the end.
        #Want to greatly minimize intents so they are not triggered accidentally while talking to ChatGPT
        #Right now we start with a button to ask if email transcipt.  Buttons = 100% confidence.  Keeping their answer in a slot in form
        #We could give them a button after each response asking if they want to end conversation and send email.
        openai.api_key = os.getenv("OPENAI_API_KEY")
        print("HELLO, we will put chatGPT call in this function!" + openai.api_key)
        
        #probably need to set this so does something different first time through
        #best idea set a slot value from true to false that is or is not first time through
        userPrompt = tracker.latest_message["text"]
        print("Last message was " + userPrompt)

	#Potential problem with formatting userPrompt this line gives chatGPT a history of user messages
        messageBase.append({"role":"user", "content":f"{userPrompt}"},)
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messageBase, temperature=0
        #model="gpt-3.5-turbo", messages=[{"role":"user", "content":f"{userPrompt}"},], temperature=0
        )
        print("after message object")
        # Creates/Open function to open the file "conversation_[senderID].txt" 
        # with the senderID being unique to each user
        uniqueFile = "conversationLogs/conversation_" + tracker.sender_id + ".txt"
        conversation_txt = open(uniqueFile,"a")
        print("conversation file should be conversation_" + tracker.sender_id +".txt")
        # write latest conversations to txt file
        # Get last conversation for bot
        for event in tracker.events:
            if (event.get("event") == "bot"):
                lastBotMessage = "Assistant message: " + event.get("text")
                conversation_txt.write("\n" + lastBotMessage)
                conversation_txt.write("\nStudent message: " + userPrompt)
        conversation_txt.close()
        print("after for loop")
        #This gives the bot a memory of its own responses
        tempBotMessage=response['choices'][0]['message']['content']
        messageBase.append({"role":"assistant", "content":f"{tempBotMessage}"},)
        print("Before removing element 1 twice")
        print(messageBase)
        #Here we are making sure the message thread never gets too long
        if len(messageBase)>=11:
            messageBase.pop(1)
            messageBase.pop(1)
        print("After removing element 1 twice")
        print(messageBase)
        #Try putting a statement here where if last message was /quit, some way to open our transcript/email form.
        if userPrompt == "/quit":
            # write latest conversations to txt file
            # Get last conversation for bot
            conversation_txt = open(uniqueFile,"a")
            for event in tracker.events:
                if (event.get("event") == "bot"):
                    lastBotMessage = "Assistant message: " + event.get("text")
            conversation_txt.close()
            print("in if statement")
            return[FollowupAction("email_form")]

        else:
            dispatcher.utter_message(text="" + response['choices'][0]['message']['content'])
            return[Restarted()]

class FindEmailIntent(Action):
  
    def name(self) -> Text:
         # Name of the action
        return "email_intent"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("We are in the find email intent custom action")
        if (tracker.get_slot("desire_send_email") == True):
           print("Found desire send email is True")
           return [FollowupAction("choose_professor_email_form")]
        else:
           print("Else statement in the find email intent custom action")
           return [Restarted(), FollowupAction("action_delete_conversation_txt"), FollowupAction("utter_goodbye")]

#class EmailIntentYes(Action):
#  
#    def name(self) -> Text:
         # Name of the action
#        return "email_intent_yes"
  
#    def run(self, dispatcher: CollectingDispatcher,
#            tracker: Tracker,
#            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#        print("Email intent is Yes!")
#        buttons = []
        #append the response of API in the form of title and payload
#        buttons.append({"title": 'Prof Meguro' , "payload": '/inform_meguro'})
#        buttons.append({"title": 'Prof Bates' , "payload": '/inform_bates'})
        #then display it using dispatcher
#        dispatcher.utter_message(text="Who is your professor?" , buttons=buttons)
#        print("After buttons")
#        return[]

 
# class ActionTest(Action):
#
#     def name(self) -> Text:
#         return "action_test"
#
#     def run(self, dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         print("HELLO this is a test action")
#         return[]
