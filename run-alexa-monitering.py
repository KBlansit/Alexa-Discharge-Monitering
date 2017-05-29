#!/usr/bin/env python

# load libraries
import yaml
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

# load user defined libraries
from src.utilities import load_questions, critical_questions

# flask initialize
app = Flask(__name__)
ask = Ask(app, '/')

# define global vars
SETTNGS_PATH = "resources/application_settings.yaml"

# temporary vars for testing and design
LIST_OF_QS = [
    "person_confirmation",
    "moving_question",
    "eating_question",
    "drinking_question",
    "pain_control_question",
]

# functions
def initialize_generic_intent(type):
    # assert that user is either a care_taker or patient
    if user not in ["care_taker", "patient"]:
        raise AssertionError("Must be either a care_taker or patient")

# define welcome message
@ask.launch
def welcome_msg():
    """
    initial hook for alexa program
    """
    # make welcome message
    speech_text = "Welcome to the discharge monitering application.\
    Is this Kevin or his caretaker?"

    return question(speech_text)

# either define question list either for patients or care taker
@ask.intent("PatientIntent")
def set_patient_session():
    # load data
    try:
        with open(SETTNGS_PATH, "r") as f:
            data = yaml.load(f)
    except IOError:
        raise IOError("Cannot locate path: " + str(path))

    # set session variables
    # set question information
    session.attributes['question_ids'] = LIST_OF_QS
    session.attributes['crit_qs'] = critical_questions(data, LIST_OF_QS)
    session.attributes['question_lst'] = load_questions(data, "patient", LIST_OF_QS)
    session.attributes['crit'] = "NON_CRIT"

    # set user level information
    session.attributes['response_recorder'] = 'self'


    # test if there's any more questions left
    if len(session.attributes['question_lst']):
        # set a hard stop warning to session
        if session.attributes['question_ids'].pop in session.attributes['crit_qs']:
            session.attributes['crit'] = "CRIT"

        # determine question text
        question_text = session.attributes['question_lst'].pop()
        return question(question_text)

@ask.intent("CareTakerIntent")
def set_patient_session():
    pass

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
