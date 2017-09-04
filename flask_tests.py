#!/usr/bin/env python

# load libraries
import io
import six
import sys
import json
import yaml
import signal
import unittest
import requests

from flask import Flask
from datetime import datetime
from requests.exceptions import Timeout
from flask_sqlalchemy import SQLAlchemy


# load user defined libraries
from webapp import ask, create_test_app

from src.Questionaire import QuestionContainer
from src.fhir_utilities import read_json_patient, create_question_response
from src.database import metadata, User, Question, IndicationQuestionOrder, SessionState, UserAnswer
from src.utilities import load_settings_and_content, load_questions, extract_questionnaire_questions

# utility functions and global vars
SETTINGS_PATH = ('resources/application_settings.yaml')
QUESTION_CONTAINER = QuestionContainer(SETTINGS_PATH)

ADMIN_QUESTION_MAP = {
    'PATIENT_CONSENT': 'welcome_text',
    'PATIENT_CONFIRMATION': 'user_identification',
    'PATIENT_2ND_CONFIRMATION': 'user_2nd_step_identification',
}

BASE_SERVICE_REQUEST = "json_fixtures/base_service_request.json"
def construct_session_request_json(intent, slot=None, question_lst=None):
    """
    INPUTS:
        intent:
            the intent to use
        question_lst:
            the question list to add to session attributes
    OUTPUT:
        a dict object which expands a base service request
        note: if question_lst is empty an empty list is constructed
    """
    # may need to remove some of this stuff when sanitizing for HIPPA

    path = BASE_SERVICE_REQUEST

    # read in json file
    with open(path) as data_file:
        body = data_file.read()
        data = json.loads(body)

    # initialize session attributes and set intent and slots
    data['request']['intent'] = {}
    data['request']['intent']['name'] = intent

    # set slot
    if slot is None:
        data['request']['intent']['slots'] = {}
    elif type(slot) is dict:
        data['request']['intent']['slots'] = slot
    else:
        raise AssertionError('question_lst must be list or None')

    # initialize session attributes
    data['session']['attributes'] = {}

    # setting of question_lst with validation
    if question_lst is None:
        data['session']['attributes']['question_lst'] = []
    elif type(question_lst) is list:
        data['session']['attributes']['question_lst'] = question_lst
    else:
        raise AssertionError('question_lst must be list or None')

    # setting of initialized
    data['session']['attributes']['initialized'] = False
    data['session']['attributes']['FHIR'] = {}

    return data

# main test definations
class TestQuestionsStructure(unittest.TestCase):

    def test_load_questions(self):
        """
        Tests that can load the content and settings yaml file
        """
        # load data
        path = "resources/application_settings.yaml"
        indication = "ileostomy"

        # cast to Questionaire container
        q_containter = QuestionContainer(path)

        # test that bad questions/statements properly rasie AssertionError
        try:
            self.assertRaises(AssertionError, q_containter.get_admin_question("BAD"))
            self.assertRaises(AssertionError, q_containter.get_admin_response("BAD"))
            self.assertRaises(AssertionError, q_containter.get_clinical_question("BAD"))
        except AssertionError:
            pass

        # verify we can get questions
        q_containter.get_list_of_clinical_questions(indication)

        tst_admin_qs = q_containter.admin_questions.keys()
        tst_admin_Ss = q_containter.admin_statements.keys()
        tst_clin_qs = q_containter.indication_questions[indication]

        for q in tst_admin_qs:
            q_containter.get_admin_question(q)
        for s in tst_admin_Ss:
            q_containter.get_admin_response(s)
        for q in tst_clin_qs:
            q_containter.get_clinical_question(q)

class TestFhirHelperMethods(unittest.TestCase):
    """
    note: requires connection to internet
    """

    def _try_twice_request(self, url, content):
        """
        try connecting twice
        """
        try:
            r = requests.post(url, data=content, timeout = 2)
        except Timeout:
            # try again
            r = requests.post(url, data=content, timeout = 2)
        return r

    def setUp(self):
        self.answer_dict = {
            "BoolQuestion1": True,
            "BoolQuestion2": False,
        }

        # read in and cast patient
        json_path = "example_fhir/ex_patient.json"
        self.example_pt = read_json_patient(json_path)

    def test_example_patient(self):
        # post to fhir server
        post_url = 'http://fhirtest.uhn.ca/baseDstu3/Patient?_format=json&_pretty=true'

        # assert we got a valid response
        r = self._try_twice_request(post_url, json.dumps(self.example_pt.as_json()))
        self.assertTrue(r.ok)

    def test_create_question_response_object(self):
        # create object
        qr = create_question_response(self.answer_dict, "completed", self.example_pt)

        # test that values are same as answer_dict

        # test that we can post to fhir server
        post_url = 'http://fhirtest.uhn.ca/baseDstu3/QuestionnaireResponse?_format=json&_pretty=true'
        r = self._try_twice_request(post_url, json.dumps(qr.as_json()))
        self.assertTrue(r.ok)

class TestAlexaServer(unittest.TestCase):
    def _initialize_session_state_db(self, session_id = "XXXXX", curr_session_state=None):
        """
        INPUTS:
            session_id:
                the session id to initialize
            curr_session_state:
                the session state to initialize
        EFFECT:
            helps initialize session db
        """
        # determine user
        curr_usr = self.db.session.query(User).filter(User.patient_f_name == "Jon").first()

        # get current pos
        qry = self.db.session.query(IndicationQuestionOrder)
        curr_pos = qry.filter(IndicationQuestionOrder.indication=='ileostomy', IndicationQuestionOrder.previous_item == None).first()

        # make session object
        curr_session = SessionState(curr_usr, session_id, curr_pos)

        # add session state if specified
        if curr_session_state:
            curr_session.session_state = curr_session_state

        # add to database
        self.db.session.add(curr_session)

    def _validate_state(self, expected_state, session_id = "XXXXX"):
        """
        INPUTS:
            expected_state:
                the expected state to initialize
            session_id:
                the session id to initialize
        EFFECT:
            validates the session state
        """
        # confirm that we switch mode
        validation_qry = self.db.session.query(SessionState).filter(SessionState.session_id=='XXXXX')
        rslt = validation_qry.all()
        if len(rslt) == 1:
            self.assertEqual(rslt[0].session_state, expected_state)
        else:
            raise AssertionError("Should only get a single result back! Got {} back instead".format(len(rslt)))

    def setUp(self):
        # initialize app and db objects
        self.app, self.db = create_test_app()
        self.app = self.app.test_client()

        # initialize db
        self.db.create_all()

        # load test data
        curr_f_user = "Jon"
        curr_l_name = "Snow"
        curr_procedure = "ileostomy"
        curr_bday = datetime.strptime("1990-10-10", "%Y-%m-%d")

        # define test objects
        usr = User(
            curr_f_user,
            curr_f_user,
            curr_bday,
            curr_procedure,
        )

        qst_1 = Question(
            q_link_id="Surg1",
            q_text="Test question 1",
            q_type="Bool",
        )

        qst_2 = Question(
            q_link_id="Surg2",
            q_text="Test question 2",
            q_type="Bool",
        )

        qst_3 = Question(
            q_link_id="Surg3",
            q_text="Test question 3",
            q_type="Bool",
        )

        indication_order_3 = IndicationQuestionOrder(
            indication=curr_procedure,
            next_item=None,
            question=qst_3,
        )

        indication_order_2 = IndicationQuestionOrder(
            indication=curr_procedure,
            next_item=indication_order_3,
            question=qst_2,
        )

        indication_order_1 = IndicationQuestionOrder(
            indication=curr_procedure,
            next_item=indication_order_2,
            question=qst_1,
        )

        # add to db
        self.db.session.add_all((
            usr,
            qst_1,
            qst_2,
            qst_3,
            indication_order_1,
            indication_order_2,
            indication_order_3,
        ))
        self.db.session.commit()

    def test_launch(self):
        # load data
        with open('json_fixtures/launch.json') as data_file:
            body = data_file.read()

        # test that we can get response back
        launch_response = self.app.post('/', data=json.dumps(json.loads(body)))
        self.assertEqual(launch_response.status_code, 200)

        # assert that we're starting the interaction
        response_data = json.loads(launch_response.get_data(as_text=True))

        # do not want to end here
        self.assertFalse(response_data['response']['shouldEndSession'])

        # verify we ask the correct question
        self.assertEqual(
            response_data['response']['outputSpeech']['text'],
            QUESTION_CONTAINER.get_admin_question('welcome_text'),
        )

        # assert we have made a session state
        self.assertTrue(len(self.db.session.query(SessionState).all()))

    def test_user_verification(self):
        # initialize session state
        self._initialize_session_state_db(curr_session_state='PATIENT_CONSENT')

        # load json format
        body = construct_session_request_json(
            intent='YesIntent',
        )

        # test that we can get response back
        confirmation_response = self.app.post('/', data=json.dumps(body))

        #import pdb; pdb.set_trace()
        self.assertEqual(confirmation_response.status_code, 200)

        # do not want to end here
        response_data = json.loads(confirmation_response.get_data(as_text=True))
        self.assertFalse(response_data['response']['shouldEndSession'])

        # verify we ask the correct question
        self.assertEqual(
            response_data['response']['outputSpeech']['text'],
            QUESTION_CONTAINER.get_admin_question('user_identification'),
        )

        # confirm that we switch mode
        self._validate_state('PATIENT_CONFIRMATION')

    def test_user_bday_verification(self):
        # initialize session state
        self._initialize_session_state_db(curr_session_state='PATIENT_2ND_CONFIRMATION')

        # define date
        bday_date = '1990-10-10'

        # load json format
        body = construct_session_request_json(
            intent='DateSlotIntent',
            question_lst=['mobility', 'pain_calves'],
            slot={'date': {'name': 'date', 'value': bday_date}},
        )

        # test that we can get response back
        confirmation_response = self.app.post('/', data=json.dumps(body))
        self.assertEqual(confirmation_response.status_code, 200)

        # do not want to end here
        response_data = json.loads(confirmation_response.get_data(as_text=True))
        self.assertFalse(response_data['response']['shouldEndSession'])

        # verify state progression
        self._validate_state('QUESTION_ITERATIONS')

    def test_bad_user_bday_verification(self):
        # initialize session state
        self._initialize_session_state_db(curr_session_state='PATIENT_2ND_CONFIRMATION')

        # define date
        bday_date = '1987-12-12'

        # load json format
        body = construct_session_request_json(
            intent='DateSlotIntent',
            question_lst=['mobility', 'pain_calves'],
            slot={'date': {'name': 'date', 'value': bday_date}},
        )

        # test that we can get response back
        confirmation_response = self.app.post('/', data=json.dumps(body))
        self.assertEqual(confirmation_response.status_code, 200)

        # want to ensure we end here
        response_data = json.loads(confirmation_response.get_data(as_text=True))
        self.assertTrue(response_data['response']['shouldEndSession'])

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

class TestWebAppDB(unittest.TestCase):
    def setUp(self):
        """
        Creates a new database for the unit test to use
        """
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['ASK_VERIFY_REQUESTS'] = False #HACK: remove for production

        # initialize db
        self.db = SQLAlchemy(app, metadata=metadata)
        self.db.create_all()

    def test_add_user(self):
        # set test user
        bdate = datetime.strptime("1990-10-10", "%Y-%m-%d")
        usr = User(
            patient_f_name='Jon',
            patient_l_name='Snow',
            patient_bday=bdate,
            patient_procedure='surg',
        )

        # pass to database
        self.db.session.add(usr)
        self.db.session.commit()

        self.assertTrue(len(self.db.session.query(User).all()) == 1)

    def test_add_question(self):
        # set test question
        tst_q_text = "This is a test question"
        tst_question = Question(
            q_link_id="Surg1",
            q_text=tst_q_text,
            q_type="Surg",
        )

        # pass to database
        self.db.session.add(tst_question)
        self.db.session.commit()

        # assert we can get question back
        self.assertTrue(len(self.db.session.query(Question).all()) == 1)
        qry = self.db.session.query(Question, Question.q_link_id=="Surg1`").first()
        self.assertEqual(qry.Question.q_text, tst_q_text)

    def test_indication_question_order(self):
        tst_question1 = Question(
            q_link_id="Surg1",
            q_text="text 1",
            q_type="Bool",
        )
        tst_question2 = Question(
            q_link_id="Surg2",
            q_text="text 2",
            q_type="Bool",
        )

        # have to work backwards
        q_order_2 = IndicationQuestionOrder(
            indication="surg",
            next_item=None,
            question=tst_question2,
        )
        q_order_1 = IndicationQuestionOrder(
            indication="surg",
            next_item=q_order_2,
            question=tst_question1,
        )
        q_order_bad_2 = IndicationQuestionOrder(
            indication="bad",
            next_item=None,
            question=tst_question2,
        )
        q_order_bad_1 = IndicationQuestionOrder(
            indication="bad",
            next_item=q_order_2,
            question=tst_question1,
        )

        # pass to database
        self.db.session.add_all((
            tst_question1,
            tst_question2,
            q_order_2,
            q_order_1,
        ))
        self.db.session.commit()

        # define query for first question
        qry = self.db.session.query(IndicationQuestionOrder)
        rslts = qry.filter(IndicationQuestionOrder.indication=='surg', IndicationQuestionOrder.previous_item == None).all()
        self.assertEqual(rslts[0].question.q_link_id, "Surg1")

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        pass

if __name__ == "__main__":
    unittest.main()
