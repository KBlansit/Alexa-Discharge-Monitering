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

from requests.exceptions import Timeout

# load user defined libraries
from webapp import create_app

from src.Questionaire import QuestionContainer
from src.utilities import load_settings_and_content, load_questions, extract_questionnaire_questions
from src.fhir_utilities import read_json_patient, create_question_response

# utility functions and global vars
SETTINGS_PATH = ('resources/application_settings.yaml')
QUESTION_CONTAINER = QuestionContainer(SETTINGS_PATH)

ADMIN_QUESTION_MAP = {
    'PATIENT_CONSENT': 'welcome_text',
    'PATIENT_CONFIRMATION': 'user_identification',
    'PATIENT_2ND_CONFIRMATION': 'user_2nd_step_identification',
}

BASE_SERVICE_REQUEST = "json_fixtures/base_service_request.json"
def construct_session_request_json(intent, session_state, slot=None, question_lst=None):
    """
    INPUTS:
        intent:
            the intent to use
        session_state:
            the session state
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

    # setting of session_state
    data['session']['attributes']['session_state'] = session_state

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
    def setUp(self):
        self.app = create_app().test_client()

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

    def test_user_verification(self):
        # load json format
        body = construct_session_request_json(
            intent='YesIntent',
            session_state='PATIENT_CONSENT',
        )

        # test that we can get response back
        confirmation_response = self.app.post('/', data=json.dumps(body))
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
        self.assertEqual(response_data['sessionAttributes']['session_state'], "PATIENT_CONFIRMATION")

    def test_user_bday_verification(self):
        # define date
        bday_date = '1990-10-10'

        # load json format
        body = construct_session_request_json(
            intent='DateSlotIntent',
            session_state='PATIENT_2ND_CONFIRMATION',
            question_lst=['mobility', 'pain_calves'],
            slot={'date': {'name': 'date', 'value': bday_date}},
        )

        # test that we can get response back
        confirmation_response = self.app.post('/', data=json.dumps(body))
        self.assertEqual(confirmation_response.status_code, 200)

        # do not want to end here
        response_data = json.loads(confirmation_response.get_data(as_text=True))
        self.assertFalse(response_data['response']['shouldEndSession'])

        # confirm that we switch mode
        self.assertEqual(response_data['sessionAttributes']['session_state'], "QUESTION_ITERATIONS")

    def test_bad_user_bday_verification(self):
        # define date
        bday_date = '1987-12-12'

        # load json format
        body = construct_session_request_json(
            intent='DateSlotIntent',
            session_state='PATIENT_2ND_CONFIRMATION',
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
        # when integrating databse, close connection here
        pass

class TestWebAppDB(unittest.TestCase):
    def setUp(self):
        """
        Creates a new database for the unit test to use
        """
        webapp.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.db = SQLAlchemy(app)

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        pass

if __name__ == "__main__":
    unittest.main()
