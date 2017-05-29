#!/usr/bin/env python

# load libraries
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

# load user defined libraries
from src.utilities import load_questions

# flask initialize
app = Flask(__name__)
ask = Ask(app, '/')

# define global vars
SETTNGS_PATH = "resources/application_text.yaml"

# define welcome message
@ask.launch
def welcome_msg():

    # make welcome message
    speech_text = "Welcome to the discharge monitering application.\
    Is this Kevin or his caretaker?"

    return question(speech_text)

# either define question list either for patients or care taker
@ask.intent("PatientIntent")
def set_patient_session():
    # append to session to initialize
    session.attributes['question_lst'] = load_questions(SETTNGS_PATH, "patient")
    session.attributes['response_recorder'] = 'self'

@ask.intent("CareTakerIntent")
def set_patient_session():
    # append to session to initialize
    session.attributes['question_lst'] = load_questions(SETTNGS_PATH, "care_taker")
    session.attributes['response_recorder'] = 'care_taker'

# response to questions
@ask.intent("YesIntent")
def yes_response():
    # test the length of the list
    if len(session.attributes['question_lst']):
        question_text = session.attributes['question_lst'].pop()
        return question(question_text)
    else:
        return statement("No more questions!")

@ask.intent("YesIntent")
def no_response():
    if len(session.attributes['question_lst']):
        question_text = session.attributes['question_lst'].pop()
        return question(question_text)
    else:
        return statement("No more questions!")

if __name__ == '__main__':
    app.run()
