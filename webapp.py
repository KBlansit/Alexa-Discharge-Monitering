#!/usr/bin/env python

# load libraries
import yaml
import random
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

# load user defined libraries
from src.Questionaire import Questionaire
from src.utilities import load_settings_and_content, load_questions

# flask initialize
app = Flask(__name__)
ask = Ask(app, '/')

# define vars
SETTINGS_PATH = ('resources/application_settings.yaml')
QUESTION_CONTAINER = Questionaire(SETTINGS_PATH)

SESSION_STATES = [
    'PATIENT_CONSENT',
    'PATIENT_CONFIRMATION',
    'PATIENT__2ND_CONFIRMATION',
    'QUESTION_ITERATION',
    'END_QUESTIONS',
]

ADMIN_QUESTION_MAP = {
    'PATIENT_CONSENT': 'welcome_text',
    'PATIENT_CONFIRMATION': 'user_identification',
    'PATIENT__2ND_CONFIRMATION': 'user_2nd_step_identification',
}

# HACK until FHIR integration:
CURR_PROCEDURE = "ileostomy"

# functions
def initialize_content():
    """
    EFFECT:
        initializes session parameters
    """
    # set question information
    question_lst = QUESTION_CONTAINER.get_list_of_clinical_questions(CURR_PROCEDURE)
    session.attributes['question_lst'] = question_lst
    session.attributes['last_question'] = None

    # set session state to user identification
    session.attributes['session_state'] = 'PATIENT_CONSENT'

    # add initialized flag to session attributes
    session.attributes['initialized'] = True

    # initialize responses
    session.attributes['bool_response'] = None
    session.attributes['date_response'] = None

def reset_question():
    """
    EFFECT:
        resets session question level attributes
    """
    # initialize responses
    session.attributes['bool_response'] = None
    session.attributes['date_response'] = None

def process_session(response_type=None):
    """
    EFFECT:
        takes session attributes parameters to create a state machine
    """
    # assert that state is valid
    assert session.attributes['session_state'] in SESSION_STATES

    # validate admin questions
    if session.attributes['session_state'] in ADMIN_QUESTION_MAP.keys():
        admin_q = ADMIN_QUESTION_MAP[session.attributes['session_state']]
        QUESTION_CONTAINER.validate_admin_answer(admin_q, response_type)

    # determine state
    if session.attributes['session_state'] == 'PATIENT_CONSENT':
        # progress session state
        session.attributes['session_state'] = 'PATIENT_CONFIRMATION'

        # determine how to respond to question
        if session.attributes['bool_response']:
            rslt_txt = QUESTION_CONTAINER.get_admin_question('user_identification')
            return question(rslt_txt)
        else:
            rslt_txt = QUESTION_CONTAINER.get_admin_response('failed_user_confirmation')
            return statement(rslt_txt)

    elif session.attributes['session_state'] == 'PATIENT_CONFIRMATION':
        # determine response
        # if yes resoponse
        if session.attributes['bool_response']:
            # reset bool_response
            session.attributes['bool_response'] = None

            # determine the result question
            rslt_txt = SETTINGS['application_content']['application_text']['user_2nd_step_identification']

            return question(rslt_txt)

        # if no resoponse
        elif not session.attributes['bool_response']:
            # reset bool_response
            session.attributes['bool_response'] = None

            # determine the result question
            rslt_txt = SETTINGS['application_content']['application_text']['user_2nd_step_identification']

            return question(rslt_txt)

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
            return question(SETTINGS['application_text']['introduction_text']['additional_edu_prompt'])

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

# define welcome message
@ask.launch
def welcome_msg():
    """
    initial hook for alexa program
    """
    # initialize session
    initialize_content()

    # fetch introduction text
    rslt_txt = QUESTION_CONTAINER.get_admin_question('welcome_text')

    # return question of speech
    return question(rslt_txt)

# response to questions
@ask.intent('YesIntent')
def yes_response():
    # set answer level parameter
    session.attributes['response_type'] = "BOOL_ANSWER"
    session.attributes['bool_response'] = True

    return process_session(response_type="BOOL_ANSWER")

@ask.intent('NoIntent')
def no_response():
    # set answer level parameter
    session.attributes['response_type'] = "BOOL_ANSWER"
    session.attributes['bool_response'] = False

    return process_session(response_type="BOOL_ANSWER")

@ask.intent('DateSlotIntent')
def date_response(date):
    print "GOT DATE " + date

    # set answer level parameter
    session.attributes['response_type'] = "BOOL_ANSWER"
    session.attributes['date_response'] = date

    return process_session(response_type="DATE_ANSWER")

@ask.session_ended
def session_ended():
    return '{}', 200

if __name__ == '__main__':
    # run app
    app.run()
