#!/usr/bin/env python

# load libraries
import yaml
import random
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

# load user defined libraries
from src.utilities import load_questions, critical_questions

# flask initialize
app = Flask(__name__)
ask = Ask(app, '/')

# define global vars
SETTNGS_PATH = "resources/application_settings.yaml"
VALID_USERS = [
    'patient',
    'caretaker',
]
SESSION_STATES = [
    'USER_IDENTIFICATION',
    'PERSON_CONFIRMATION',
    'SCREENING_OR_EDU',
    'SCREENING_CONSENT',
    'SCREENING_QUESTIONS',
    ]

# HACK
# needs to be replaced with database linkage
PREVIOUSLY_PERFORMED_SCREENING = False
SESSION_PROCEDURE = "ILEOSTOMY"
LIST_OF_QS = [
    "Mobility",
    "Currently Eating",
    "Currently Drinking",
    "Currently Taking Pain Medications",

    'end_statement'
]

# functions
def question_and_answer():
    # assert that state is valid
    assert session.attributes['session_state'] in SESSION_STATES

    # load data
    try:
        with open(SETTNGS_PATH, "r") as f:
            data = yaml.load(f)
    except IOError:
        raise IOError("Cannot locate path: " + str(path))

    # determine state
    if session.attributes['session_state'] == 'USER_IDENTIFICATION':
        # set session state
        session.attributes['session_state'] = "PERSON_CONFIRMATION"

        # return text
        user = session.attributes['user']
        rslt_lst = data['application_text']['question_text']['Person Confirmation'][user]

        return question(random.choice(rslt_lst))

    elif session.attributes['session_state'] == 'PERSON_CONFIRMATION':
        # determine response
        if not session.attributes['bool_response']:

            # return text
            rslt_lst = data['application_text']['introduction_text']['failed_user_confirmation']

            return statement(rslt_lst)

        else:
            # set session state
            session.attributes['session_state'] = "SCREENING_OR_EDU"

            # return text
            rslt_lst = data['application_text']['introduction_text']['ask_screening_or_edu']

            return statement(rslt_lst)

    elif session.attributes['session_state'] == 'SCREENING_CONSENT':
        pass
    elif session.attributes['session_state'] == 'SCREENING_CONSENT':
        pass
    elif session.attributes['session_state'] == 'SCREENING_QUESTIONS':
        pass

def initialize_questions(user):
    """
    initializes session parameters for either the patienr or caretaker user
    """
    # assert that user is either a caretaker or patient
    if user not in VALID_USERS:
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

    # set critical to false
    session.attributes['crit'] = False

def consent_for_screening():
    pass

def screening_question_iteration(intent_type=None, critical_question=False):
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

def educational_response(educational_request):
    """
    """
    # load data
    try:
        with open(SETTNGS_PATH, "r") as f:
            data = yaml.load(f)
    except IOError:
        raise IOError("Cannot locate path: " + str(path))

    # subset data
    procedure_data = data['application_text']['educational_text'][SESSION_PROCEDURE]

    # check if key is in dict
    if educational_request in procedure_data.keys():
        educational_response_text = procedure_data[educational_request]['text']

        # prompt if screening not already done for screening
        # might be nice to add a MCMC model to this to ask after n edu requests
        if not PREVIOUSLY_PERFORMED_SCREENING:
            # set state to confirmation mode
            session.attributes['session_state'] = "PERSON_CONFIRMATION"

            # ask for consent to screen
            additional_text = data['application_text']['introduction_text']['prompt_for_screening']

        else:
            # ask for consent to screen
            additional_text = data['application_text']['introduction_text']['additional_edu_prompt']

        return question(educational_response_text + "..." + additional_text)

    else:
        # else return that we cannot find the specific question
        return question(data['introduction_text']['educational_content_not_found'])

# define welcome message
@ask.launch
def welcome_msg():
    """
    initial hook for alexa program
    """
    # make welcome message
    reply_text = "Welcome to the discharge monitoring application.\
    Is this Kevin or his caretaker?"

    # set state
    session.attributes['session_state'] = 'USER_IDENTIFICATION'

    # return question of speech
    return question(reply_text)

# set user for either patient or care taker
@ask.intent("PatientIntent")
def set_user_session():

    # set patient level parameter
    session.attributes['user'] = 'patient'

    # let question and state flow through custom question
    return question_and_answer()

@ask.intent("CaretakerIntent")
def set_user_session():

    # set patient level parameter
    session.attributes['user'] = 'caretaker'

    # let question and state flow through custom question
    return question_and_answer()

# response to questions
@ask.intent("YesIntent")
def yes_response():
    # set answer level parameter
    session.attributes['bool_response'] = True

    return question_and_answer()

@ask.intent("NoIntent")
def no_response():
    # set answer level parameter
    session.attributes['bool_response'] = False

    return question_and_answer()

# educational_intents
@ask.intent("QuestionWoundCareIntent")
def wound_care_education():
    return educational_response("WOUND CARE")

@ask.session_ended
def session_ended():
    return "{}", 200

if __name__ == '__main__':
    app.run()
