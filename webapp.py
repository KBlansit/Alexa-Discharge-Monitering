#!/usr/bin/env python

# load libraries
import yaml
import random
from datetime import datetime
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

# load user defined libraries
from src.Questionaire import QuestionContainer
from src.utilities import load_settings_and_content, load_questions
from src.fhir_utilities import read_json_patient

# flask initialize
app = Flask(__name__)
app.config['ASK_VERIFY_REQUESTS'] = False #HACK: remove for production
ask = Ask(app, '/')

# fhir
FHIR_SUBJECT = read_json_patient('example_fhir/ex_patient.json')

# define vars
SETTINGS_PATH = ('resources/application_settings.yaml')
QUESTION_CONTAINER = QuestionContainer(SETTINGS_PATH)

SESSION_STATES = [
    'PATIENT_CONSENT',
    'PATIENT_CONFIRMATION',
    'PATIENT_2ND_CONFIRMATION',
    'QUESTION_ITERATIONS',
    'END_QUESTIONS',
]

ADMIN_QUESTION_MAP = {
    'PATIENT_CONSENT': 'welcome_text',
    'PATIENT_CONFIRMATION': 'user_identification',
    'PATIENT_2ND_CONFIRMATION': 'user_2nd_step_identification',
}

# HACK until FHIR integration:
CURR_PROCEDURE = "ileostomy"
CURR_USER = "Jon"
CURR_BDAY = datetime.strptime("1990-10-10", "%Y-%m-%d")

# functions
def initialize_content():
    """
    EFFECT:
        initializes session parameters
    """
    # set question information
    question_lst = QUESTION_CONTAINER.get_list_of_clinical_questions(CURR_PROCEDURE)
    session.attributes['question_lst'] = question_lst
    session.attributes['previous_question'] = None

    # set session state to user identification
    session.attributes['session_state'] = 'PATIENT_CONSENT'

    # add initialized flag to session attributes
    session.attributes['initialized'] = True

    # initialize responses
    session.attributes['response'] = {
        'response_slot': None,
        'response_type': None,
    }

    # initialize answers container
    session.attributes['answer_dict'] = {}

    # initialize fhir
    session.attributes['FHIR'] = {}
    session.attributes['FHIR']['subject'] = None

def reset_question():
    """
    EFFECT:
        resets session question level attributes
    """
    # initialize responses
    session.attributes['response'] = {
        'response_slot': None,
        'response_type': None,
    }

def validate_question_answer():
    # validate admin questions
    if session.attributes['session_state'] in ADMIN_QUESTION_MAP.keys():
        admin_q = ADMIN_QUESTION_MAP[session.attributes['session_state']]
        response_type = session.attributes['response']['response_type']
        QUESTION_CONTAINER.validate_admin_answer(admin_q, response_type)

    return True

def process_session():
    """
    EFFECT:
        takes session attributes parameters to create a state machine
    """

    # assert that state is valid
    assert session.attributes['session_state'] in SESSION_STATES

    # validate question
    assert validate_question_answer()

    # determine state
    if session.attributes['session_state'] == 'PATIENT_CONSENT':

        # determine how to respond to question
        if session.attributes['response']['response_slot']:
            # progress session state
            session.attributes['session_state'] = 'PATIENT_CONFIRMATION'

            # ask the next question
            rslt_txt = QUESTION_CONTAINER.get_admin_question('user_identification')
            return question(rslt_txt)
        else:
            rslt_txt = QUESTION_CONTAINER.get_admin_response('failed_user_confirmation')
            return statement(rslt_txt)

    elif session.attributes['session_state'] == 'PATIENT_CONFIRMATION':

        # determine how to respond to question
        if session.attributes['response']['response_slot']:
            # progress session state
            session.attributes['session_state'] = 'PATIENT_2ND_CONFIRMATION'

            # ask the next question
            rslt_txt = QUESTION_CONTAINER.get_admin_question('user_2nd_step_identification')
            return question(rslt_txt)
        else:
            rslt_txt = QUESTION_CONTAINER.get_admin_response('failed_user_confirmation')
            return statement(rslt_txt)

    elif session.attributes['session_state'] == 'PATIENT_2ND_CONFIRMATION':
        # format date
        input_date = datetime.strptime(session.attributes['response']['response_slot'], "%Y-%m-%d")

        # determine how to respond to question
        if input_date.date() == CURR_BDAY.date():
            # progress session state
            session.attributes['session_state'] = 'QUESTION_ITERATIONS'

            # add fhir info to session
            session.attributes['FHIR']['subject'] = FHIR_SUBJECT.as_json()

            # populate question list
            if len(session.attributes['question_lst']):
                # determine question text
                curr_question = session.attributes['question_lst'].pop()
                session.attributes['previous_question'] = curr_question
                question_txt = QUESTION_CONTAINER.get_clinical_question(curr_question)

                return question(question_txt)
            else:
                rslt_txt = QUESTION_CONTAINER.get_admin_response('failed_user_confirmation')
                return statement(rslt_txt)
        else:
            rslt_txt = QUESTION_CONTAINER.get_admin_response('failed_user_confirmation')
            return statement(rslt_txt)

    elif session.attributes['session_state'] == 'QUESTION_ITERATIONS':
        # record answer
        if session.attributes['response']['response_type'] == "BOOL_ANSWER":
            session.attributes['answer_dict'][session.attributes['previous_question']] = session.attributes['response']['response_slot']

        # determine is session progresses (next to last)
        if len(session.attributes['question_lst']) == 1:
            session.attributes['session_state'] = 'END_QUESTIONS'

        # determine question text
        curr_question = session.attributes['question_lst'].pop()
        session.attributes['previous_question'] = curr_question
        question_txt = QUESTION_CONTAINER.get_clinical_question(curr_question)

        return question(question_txt)

    elif session.attributes['session_state'] == 'END_QUESTIONS':
        # record answer
        if session.attributes['response']['response_type'] == "BOOL_ANSWER":
            session.attributes['answer_dict'][session.attributes['previous_question']] = session.attributes['response']['response_slot']

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
    # reset enviorment
    reset_question()

    # set answer level parameter
    session.attributes['response']['response_slot'] = True
    session.attributes['response']['response_type'] = "BOOL_ANSWER"

    return process_session()

@ask.intent('NoIntent')
def no_response():
    # reset enviorment
    reset_question()

    # set answer level parameter
    session.attributes['response']['response_slot'] = False
    session.attributes['response']['response_type'] = "BOOL_ANSWER"

    return process_session()

@ask.intent('DateSlotIntent')
def date_response(date):
    # reset enviorment
    reset_question()

    # set answer level parameter
    session.attributes['response']['response_slot'] = date
    session.attributes['response']['response_type'] = "DATE_ANSWER"

    return process_session()

@ask.session_ended
def session_ended():
    return '{}', 200

if __name__ == '__main__':
    # run app
    app.run()
