#!/usr/bin/env python

# load libraries
from flask import Flask
from flask_ask import Ask, statement, question, session

# flask initialize
app = Flask(__name__)
ask = Ask(app, '/')

# define current user
curr_user = None

#HACK
question1 = "Question one"
question2 = "Question two"
question3 = "Question three"

# append to session
session = [question1, question2, question3]

# define welcome message
@ask.launch
def welcome_msg():
    # make welcome message
    speech_text = "Welcome to the discharge monitering application.\
    Is this Kevin or his caretaker?"

    return question(speech_text)

# First level of question
# define intents
@ask.intent("CareTakerIntent")
def verify_user():
    # set curr_user as caretaker
    curr_user = "CARE_TAKER"

    # confirmation that we're talking about the correct person

    return question(speech_text)

if __name__ == '__main__':
    app.run()
