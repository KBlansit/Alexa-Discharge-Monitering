#!/usr/bin/env python

# load libraries
import yaml
import random
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

# load user defined libraries
from src.utilities import load_settings_and_content, load_questions

# flask initialize
app = Flask(__name__)
ask = Ask(app, '/')

# define vars
SETTINGS = load_settings_and_content('resources/application_settings.yaml')

SESSION_STATES = [
    'PATIENT_CONSENT',
    'PATIENT_CONFIRMATION',
    'PATIENT__2ND_CONFIRMATION',
    'QUESTION_ITERATION',
    'END_QUESTIONS',
]

# HACK until FHIR integration:
CURR_PROCEDURE = "ileostomy"

# functions
def initialize_content():
    """
    EFFECT:
        initializes session parameters
    """
    # set question information
    session.attributes['question_lst'] = load_questions(SETTINGS, CURR_PROCEDURE)

    # set session state to user identification
    session.attributes['session_state'] = 'PATIENT_CONSENT'

    # add initialized flag to session attributes
    session.attributes['initialized'] = True

    # initialize responses
    session.attributes['response_type'] = None
    session.attributes['bool_response'] = None
    session.attributes['date_response'] = None

def resolve_answer():
    """
    EFFECT:
        resolves the answer from the user
    """

def question_and_answer():
    """
    EFFECT:
        takes session attributes parameters to create a state machine
    """
    # assert that state is valid
    assert session.attributes['session_state'] in SESSION_STATES

    # determine state
    if session.attributes['session_state'] == 'PATIENT_CONSENT':
        # progress session state
        session.attributes['session_state'] = 'PATIENT_CONFIRMATION'

        # determine the result question
        rslt_txt = SETTINGS['application_content']['application_text']['user_identification']

        return question(rslt_txt)

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
    rslt_txt = SETTINGS['application_content']['application_text']['welcome_text']

    # return question of speech
    return question(rslt_txt)

# response to questions
@ask.intent('YesIntent')
def yes_response():
    # set answer level parameter
    session.attributes['response_type'] = "BOOL_ANSWER"
    session.attributes['bool_response'] = True

    return question_and_answer()

@ask.intent('NoIntent')
def no_response():
    # set answer level parameter
    session.attributes['response_type'] = "BOOL_ANSWER"
    session.attributes['bool_response'] = False

    return question_and_answer()

@ask.intent('DateSlotIntent')
def date_response(date):
    print "GOT DATE " + date

    # set answer level parameter
    session.attributes['response_type'] = "BOOL_ANSWER"
    session.attributes['date_response'] = date

    return question_and_answer()

@ask.session_ended
def session_ended():
    return '{}', 200

if __name__ == '__main__':
    # run app
    app.run()
