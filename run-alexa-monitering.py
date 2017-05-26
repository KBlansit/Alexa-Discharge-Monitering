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
session.attributes['question_lst'] = [question1, question2, question3]

# define welcome message
@ask.launch
def welcome_msg():
    # make welcome message
    speech_text = "Welcome to the discharge monitering application.\
    Is this Kevin or his caretaker?"

    return question(speech_text)

# First level of question
# define intents
@ask.intent("NextIntent")
def loop_through_questions():

    # test the length of the list
    if len(session.attributes['question_lst'].pop()):
        question_text = session.attributes['question_lst'].pop()
        return question(speech_text)
    else:
        return statement("No more questions!")

if __name__ == '__main__':
    app.run()
