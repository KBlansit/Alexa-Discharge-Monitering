#!/usr/bin/env python

# load libraries
from flask import Flask
from flask_ask import Ask, statement, question, session

# flask initialize
app = Flask(__name__)
ask = Ask(app, '/')

@ask.launch
def welcome_msg():
    speech_text = "Welcome to the discharge monitering application.\
    Is this Kevin or his caretaker?"
    return question(speech_text)

@ask.intent("CareTakerIntent")
def

if __name__ == '__main__':
    app.run()
