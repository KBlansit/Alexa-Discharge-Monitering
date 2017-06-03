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
    "Person Confirmation",
    "Mobility",
    "Currently Eating",
    "Currently Drinking",
    "Currently Taking Pain Medications",

    'end_statement'
]

# functions
def initialize_session_parameters(user):
    """
    initializes session parameters for either the patienr or caretaker user
    """
    # assert that user is either a caretaker or patient
    if user not in ["caretaker", "patient"]:
        raise AssertionError("Must be either a caretaker or patient")

    # load data
    try:
        with open(SETTNGS_PATH, "r") as f:
            data = yaml.load(f)
    except IOError:
        raise IOError("Cannot locate path: " + str(path))

    # set question information
    session.attributes['question_lst'] = load_questions(data, user, LIST_OF_QS)

    # set user recorder information
    session.attributes['response_recorder'] = user

    # initialize end statement
    #print data['application_text']['end_statement']
    #session.attributes['end_statement'] = data['application_text']['end_statement'][user][0]

    # set critical to false
    session.attributes['crit'] = False
    session.attributes['initialized'] = True

def question_iteration(intent_type=None, critical_question=False):
    """
    used to iterate through questions
    """

    # assert initialized
    if not hasattr(session.attributes, 'initialized'):
        raise AssertionError("Used an utterance before initialization")

    if not session.attributes['initialized']:
        raise AssertionError("Used an utterance before initialization")

    # if critical question is answered no, then end
    if session.attributes['crit'] and intent_type is "no":
        return statement("Hmmm... something appears to be wrong")

    # set critical question
    session.attributes['crit'] = critical_question

    # test if there's any more questions left
    if len(session.attributes['question_lst']):
        # determine question text
        question_text = session.attributes['question_lst'].pop()
        return question(question_text)
    else:
        return statement("Great! I'll send these results to your doctor, and will\
                         contact you if there's any more information we need.")

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

# either define question list either for patients or caretaker
@ask.intent("PatientIntent")
def set_patient_session():
    initialize_session_parameters("patient")
    return question_iteration(critical_question=True)

@ask.intent("CaretakerIntent")
def set_patient_session():
    initialize_session_parameters("caretaker")
    return question_iteration(critical_question=True)

# response to questions
@ask.intent("YesIntent")
def yes_response():
    return question_iteration("yes")

@ask.intent("NoIntent")
def no_response():
    return question_iteration("no")

@ask.session_ended
def session_ended():
    return "{}", 200

if __name__ == '__main__':
    app.run()
