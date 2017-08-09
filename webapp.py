#!/usr/bin/env python

# load libraries
import yaml
import random

from datetime import datetime

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# load user defined libraries
from src.Questionaire import QuestionContainer
from src.utilities import load_settings_and_content, load_questions
from src.fhir_utilities import read_json_patient
from src.model import db

# initialize extention objects
ask = Ask(route = '/')
db = SQLAlchemy()

# flask initialize
def create_app():
    # initialize flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['ASK_VERIFY_REQUESTS'] = False #HACK: remove for production

    # initialize flask extentions
    db.init_app(app)
    ask.init_app(app)

    return app


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
CURR_USER = "Jon"
CURR_L_NAME = "SNOW"
CURR_PROCEDURE = "ileostomy"
CURR_USER = "Jon"
CURR_BDAY = datetime.strptime("1990-10-10", "%Y-%m-%d")

class User(db.Model):
    # define model items
    id = db.Column(db.Integer, primary_key=True)
    patient_f_name = db.Column(db.String(80))
    patient_l_name = db.Column(db.String(80))
    patient_bday = db.Column(db.Date)
    patient_procedure = db.Column(db.String(80))

    def __init__(
        self,
        patient_f_name,
        patient_l_name,
        patient_bday,
        patient_procedure,
    ):
        self.patient_f_name = patient_f_name
        self.patient_l_name = patient_l_name
        self.patient_bday = patient_bday
        self.patient_procedure = patient_procedure

    def __repr__(self):
        return '<User: {} {}>'.format(self.patient_f_name, self.patient_l_name)

class Question(db.Model):
    # define model items
    id = db.Column(db.Integer, primary_key=True)
    q_link_id = db.Column(db.String(80))
    q_text = db.Column(db.Text)
    q_type = db.Column(db.String(80))

    def __init__(
        self,
        q_link_id,
        q_text,
        q_type,
    ):
        self.q_link_id = q_link_id
        self.q_text = q_text

    def __repr__(self):
        return '<QuestionID: {}>'.format(self.q_link_id)

class IndicationQuestionOrder(db.Model):
    __tablename__ = 'indicationquestionorder'

    # define model items
    id = db.Column(db.Integer, primary_key=True)
    indication = db.Column(db.String(80))
    question_id = db.Column(db.Integer, db.ForeignKey(Question.id))
    question = db.relationship("Question")

    def __init__(
        self,
        indication,
        next_item,
        question,
    ):
        self.indication = indication
        self.next_item = next_item
        self.question = question

    def __repr__(self):
        return '<Indication: {}, Question: {}>'.format(self.indication, self.question)

# monkey patch
IndicationQuestionOrder.next_id = db.Column(db.Integer, db.ForeignKey(IndicationQuestionOrder.id))
IndicationQuestionOrder.next_item = db.relationship(IndicationQuestionOrder, backref = "previous_item", remote_side = IndicationQuestionOrder.id)

class SessionState(db.Model):
    # define model items
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship("User")
    session_id = db.Column(db.String(80))
    curr_list_position_id = db.Column(db.Integer, db.ForeignKey(IndicationQuestionOrder.id))
    curr_list_position = db.relationship("IndicationQuestionOrder")

    session_state = db.Column(db.String(80))
    active = db.Column(db.Boolean)

    def __init__(
        user,
        session_id,
        curr_list_position,
    ):
        # from constructor
        self.user = user
        self.session_id = session_id
        self.curr_list_position = curr_list_position

        # defaults
        self.session_state = 'PATIENT_CONSENT'
        self.active = True

    def __repr__(self):
        return '<Session: {}, State: {}>'.format(self.session_id, self.session_state)

class UserAnswer(db.Model):
    # define model items
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship("User")
    question_id = db.Column(db.Integer, db.ForeignKey(Question.id))
    question = db.relationship("Question")
    answer_bool = db.Column(db.Boolean)

    def __init__(
        self,
        user,
        question,
        answer_bool = None,
    ):
        self.user = user
        self.question = question
        self.answer_bool = answer_bool

    def __repr__(self):
        return '<User: {}, Answer: {}>'.format(self.user, self.answer_bool)

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
    app = create_app()
    app.run()
