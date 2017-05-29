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
def initialize_session_parameters(user):
    # assert that user is either a care_taker or patient
    if user not in ["care_taker", "patient"]:
        raise AssertionError("Must be either a care_taker or patient")

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
    session.attributes['question_lst'] = load_questions(data, user, LIST_OF_QS)
    session.attributes['crit'] = "non-critical"

    # set user level information
    session.attributes['response_recorder'] = user

def question_iteration(intent_type=None):
    # if critical question is answered no, then end
    if session.attributes['crit'] is "CRIT" and intent_type is "no":
        return statement("Hmmm... something appears to be wrong")

    # test if there's any more questions left
    if len(session.attributes['question_lst']):
        # set a hard stop warning to session
        if session.attributes['question_ids'].pop in session.attributes['crit_qs']:
            session.attributes['crit'] = "CRIT"

        # determine question text
        question_text = session.attributes['question_lst'].pop()
        return question(question_text)

# define welcome message
@ask.launch
def welcome_msg():
    """
    initial hook for alexa program
    """
    # make welcome message
    speech_text = "Welcome to the discharge monitoring application.\
    Is this Kevin or his caretaker?"

    return question(speech_text)

# either define question list either for patients or care taker
@ask.intent("PatientIntent")
def set_patient_session():
    initialize_session_parameters("patient")
    return question_iteration()

@ask.intent("CareTakerIntent")
def set_patient_session():
    initialize_session_parameters("care_taker")
    return question_iteration()

# response to questions
@ask.intent("YesIntent")
def yes_response():
    return question_iteration("yes")

@ask.intent("NoIntent")
def no_response():
    return question_iteration("no")

if __name__ == '__main__':
    app.run()
