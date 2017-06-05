#!/usr/bin/env python

# load libraries
import yaml
import random
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

# load user defined libraries
from src.utilities import load_questions

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
        # if yes resoponse
        if session.attributes['bool_response']:
            # reset bool_response
            session.attributes['bool_response'] = None

            # set session state
            session.attributes['session_state'] = "SCREENING_OR_EDU"

            # return text
            rslt_lst = data['application_text']['introduction_text']['ask_screening_or_edu']

            return question(rslt_lst)

        # if no resoponse
        elif not session.attributes['bool_response']:
            # reset bool_response
            session.attributes['bool_response'] = None

            # return text
            rslt_lst = data['application_text']['introduction_text']['failed_user_confirmation']

            return statement(rslt_lst)
        # otherwise raise error
        else:
            # reset bool_response
            session.attributes['bool_response'] = None

            raise AssertionError('Had trouble understanding what the response was')

    elif session.attributes['session_state'] == 'SCREENING_CONSENT':
        # determine response
        # if yes response
        if session.attributes['bool_response']:
            # reset bool_response
            session.attributes['bool_response'] = None

            # intialize questions
            initialize_questions()

            # set session state to question screening
            session.attributes['session_state'] = 'SCREENING_QUESTIONS'

            return screening_question_iteration()

        if not session.attributes['bool_response']:
            # reset bool_response
            session.attributes['bool_response'] = None

            # ask if there's anything else to do
            return question(data['application_text']['introduction_text']['additional_edu_prompt'])

        # otherwise raise error
        else:
            # reset bool_response
            session.attributes['bool_response'] = None

            raise AssertionError('Had trouble understanding what the response was')

    elif session.attributes['session_state'] == 'SCREENING_QUESTIONS':
        if session.attributes['bool_response']:
            # reset bool_response
            session.attributes['bool_response'] = None

            # ask if there's anything else to do
            return screening_question_iteration()

        if not session.attributes['bool_response']:
            # reset bool_response
            session.attributes['bool_response'] = None

            # ask if there's anything else to do
            return screening_question_iteration()

        # otherwise raise error
        else:
            # reset bool_response
            session.attributes['bool_response'] = None

            raise AssertionError('Had trouble understanding what the response was')

def initialize_questions():
    """
    initializes session parameters for either the patienr or caretaker user
    """
    # load data
    try:
        with open(SETTNGS_PATH, "r") as f:
            data = yaml.load(f)
    except IOError:
        raise IOError("Cannot locate path: " + str(path))

    user = session.attributes['user']

    # set question information
    session.attributes['question_lst'] = load_questions(data, user, SESSION_PROCEDURE)

    # set user recorder information
    session.attributes['response_recorder'] = user

def screening_question_iteration():
    """
    used to iterate through questions
    """

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
        if not PREVIOUSLY_PERFORMED_SCREENING and not session.attributes['asked_screening']:
            # don't prompt again
            session.attributes['asked_screening'] = True

            # set state to confirmation mode
            session.attributes['session_state'] = "SCREENING_CONSENT"

            # ask for consent to screen
            additional_text = data['application_text']['introduction_text']['prompt_for_screening']

        else:
            # ask for consent to screen
            additional_text = data['application_text']['introduction_text']['additional_edu_prompt']

        return question(educational_response_text + "... " + additional_text)

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

    # initialize setup
    session.attributes['session_state'] = 'USER_IDENTIFICATION'
    session.attributes['asked_screening'] = False

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

@ask.intent("ScreeningIntent")
def screening_response():
    if session.attributes['session_state'] == 'SCREENING_OR_EDU':
        # intialize questions
        initialize_questions()

        # set session state to question screening
        session.attributes['session_state'] = 'SCREENING_QUESTIONS'

        return screening_question_iteration()

    else:
        return statement("hmm... cannot do that right now")

# educational_intents
@ask.intent("QuestionWoundCareIntent")
def wound_care_education():
    return educational_response("WOUND CARE")

@ask.session_ended
def session_ended():
    return "{}", 200

if __name__ == '__main__':
    app.run()
