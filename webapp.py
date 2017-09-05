#!/usr/bin/env python

# load libraries
import yaml
import random

from datetime import datetime

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine

# load user defined libraries
from src.Questionaire import QuestionContainer
from src.utilities import load_settings_and_content, load_questions
from src.fhir_utilities import read_json_patient
from src.database import metadata
from src.database import User, Question, IndicationQuestionOrder, SessionState, UserAnswer, SESSION_STATES

# initialize extention objects
ask = Ask(route = '/')

# initialize db
db = SQLAlchemy(metadata=metadata)

# flask initialize
def create_app():
    # initialize flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ASK_VERIFY_REQUESTS'] = False #HACK: remove for production

    # bind app to db
    db.app = app # your library is bad and you should feel bad...
    db.init_app(app)

    # initialize flask extentions
    ask.init_app(app)

    return app, db

def create_test_app():
    # initialize flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ASK_VERIFY_REQUESTS'] = False #HACK: remove for production

    # bind app to db
    db.app = app # your library is bad and you should feel bad...
    db.init_app(app)

    # initialize flask extentions
    ask.init_app(app)

    return app, db

# HACK until FHIR integration:

SETTINGS_PATH = ('resources/application_settings.yaml')
QUESTION_CONTAINER = QuestionContainer(SETTINGS_PATH)

CURR_USER = "Jon"
CURR_L_NAME = "SNOW"
CURR_PROCEDURE = "ileostomy"
CURR_USER = "Jon"
CURR_BDAY = datetime.strptime("1990-10-10", "%Y-%m-%d")

# functions
def initialize_content():
    """
    EFFECT:
        initializes session parameters
    """
    # add initialized flag to session attributes
    session.attributes['initialized'] = True

    # initialize responses
    session.attributes['response'] = {
        'response_slot': None,
        'response_type': None,
    }

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

def process_session():
    """
    EFFECT:
        takes session attributes parameters to create a state machine
    """
    # get session state
    qry = db.session.query(SessionState).filter(SessionState.session_id==session.sessionId)

    # validate we have right number
    if qry.count() > 1:
        raise AssertionError("Result: {} returned multiple sessions".format(rslt))
    elif qry.count() == 0:
        raise AssertionError("Did not return any results for this session!")

    # return to object
    rslt = qry.one_or_none()

    # get session state
    state = rslt.session_state

    # assert that state is valid
    assert state in SESSION_STATES

    # determine state
    if state == 'PATIENT_CONSENT':
        # determine how to respond to question
        if session.attributes['response']['response_slot']:
            # progress session state
            rslt.session_state = 'PATIENT_CONFIRMATION'

            # add to database
            db.session.commit()
            db.session.close()

            # ask the next question
            rslt_txt = QUESTION_CONTAINER.get_admin_question('user_identification')
            return question(rslt_txt)
        else:
            rslt_txt = QUESTION_CONTAINER.get_admin_response('failed_user_confirmation')
            return statement(rslt_txt)

    elif state == 'PATIENT_CONFIRMATION':
        # determine how to respond to question
        if session.attributes['response']['response_slot']:
            # progress session state
            rslt.session_state = 'PATIENT_2ND_CONFIRMATION'

            # add to database
            db.session.commit()
            db.session.close()

            # ask the next question
            rslt_txt = QUESTION_CONTAINER.get_admin_question('user_2nd_step_identification')
            return question(rslt_txt)
        else:
            rslt_txt = QUESTION_CONTAINER.get_admin_response('failed_user_confirmation')
            return statement(rslt_txt)

    elif state == 'PATIENT_2ND_CONFIRMATION':
        # format date
        input_date = datetime.strptime(session.attributes['response']['response_slot'], "%Y-%m-%d")

        # determine how to respond to question
        if input_date.date() == CURR_BDAY.date():
            # progress session state
            rslt.session_state = 'QUESTION_ITERATIONS'

            # add to database
            db.session.commit()
            db.session.close()

            # get current position
            curr_pos = qry.one_or_none().curr_list_position
            if curr_pos.next_item is not None:
                # add question text
                question_txt = curr_pos.question.q_text

                # increment question
                next_pos = curr_pos.next_item

                # reinitialize session state to update
                curr_sess = qry.one_or_none()
                curr_sess.curr_list_position = next_pos

                # add to database
                db.session.commit()
                db.session.close()

                return question(question_txt)
            else:
                rslt_txt = QUESTION_CONTAINER.get_admin_response('failed_user_confirmation')
                return statement(rslt_txt)
        else:
            rslt_txt = QUESTION_CONTAINER.get_admin_response('failed_user_confirmation')
            return statement(rslt_txt)

    elif state == 'QUESTION_ITERATIONS':
        # get question and answer to record
        if hasattr(qry.one_or_none().curr_list_position, 'previous_item'):
            prev_question = qry.one_or_none().curr_list_position.previous_item[0].question
        else:
            raise AssertionError("Did not have a previous valid question")

        curr_user = qry.one_or_none().user

        # record answer
        if session.attributes['response']['response_type'] == "BOOL_ANSWER":
             # create answer object
             curr_answer = UserAnswer(
                 user=curr_user,
                 question=prev_question,
                 answer_bool=session.attributes['response']['response_slot']
             )
        else:
             raise AssertionError("Did not recieve valid type of answer: {}".\
                format(session.attributes['response']['response_type']))

        # add to session
        db.session.add(curr_answer)

        # get current position
        curr_pos = qry.one_or_none().curr_list_position

        # add question text
        question_txt = curr_pos.question.q_text

        # increment question
        next_pos = curr_pos.next_item

        # reinitialize session state to update
        curr_sess = qry.one_or_none()
        curr_sess.curr_list_position = next_pos

        # determine if we should progress
        if curr_pos.next_item is None:
            # progress session state
            curr_sess.session_state = 'END_QUESTIONS'

        # add to database
        db.session.commit()
        db.session.close()

        return question(question_txt)

    elif state == 'END_QUESTIONS':
        # get last question for indication
        curr_proc = qry.one_or_none().user.patient_procedure
        prev_question = db.session.query(IndicationQuestionOrder).\
            filter(
                IndicationQuestionOrder.next_item==None,
                IndicationQuestionOrder.indication==curr_proc,
            ).one_or_none().question

        # get current user
        curr_user = qry.one_or_none().user

        # record answer
        if session.attributes['response']['response_type'] == "BOOL_ANSWER":
             # create answer object
             curr_answer = UserAnswer(
                 user=curr_user,
                 question=prev_question,
                 answer_bool=session.attributes['response']['response_slot']
             )
        else:
             raise AssertionError("Did not recieve valid type of answer: {}".\
                format(session.attributes['response']['response_type']))

        # add to session
        db.session.add(curr_answer)

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

    # initialize session state
    # HACK for migration
    # get current user
    curr_usr = db.session.query(User).filter(User.patient_f_name == "Jon").first()

    # get current pos
    qry = db.session.query(IndicationQuestionOrder)
    curr_pos = qry.filter(IndicationQuestionOrder.indication=='ileostomy', IndicationQuestionOrder.previous_item == None).first()

    # make session object
    curr_session = SessionState(curr_usr, session.sessionId, curr_pos)

    # add to database
    db.session.add(curr_session)
    db.session.commit()
    db.session.close()

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
    app, db = create_app()
    app.run()
