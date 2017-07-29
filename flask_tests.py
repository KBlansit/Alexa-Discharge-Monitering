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
import webapp

from src.Questionaire import QuestionContainer
from src.utilities import load_settings_and_content, load_questions, extract_questionnaire_questions
from src.fhir_utilities import read_json_patient, create_question_response

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
        self.app = webapp.app.test_client()

    def test_launch(self):
        # load data
        with open('json_fixtures/launch.json') as data_file:
            body = data_file.read()
            rqst = io.StringIO(six.u(body))

        # test that we can get response back
        launch_response = self.app.post('/', data=json.dumps(json.loads(body)))
        self.assertEqual(launch_response.status_code, 200)

        # assert that we're starting the interaction
        response_data = json.loads(launch_response.get_data(as_text=True))

        # do not want to end here
        self.assertFalse(response_data['response']['shouldEndSession'])

    def test_(self):
        pass

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
