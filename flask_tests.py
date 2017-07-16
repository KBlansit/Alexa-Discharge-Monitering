#!/usr/bin/env python

# load libraries
import sys
import json
import yaml
import unittest
import requests

# load user defined libraries
from src.Questionaire import QuestionContainer
from src.utilities import load_settings_and_content, load_questions, extract_questionnaire_questions
from src.fhir_helper_functions import read_json_patient, create_question_response

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

class TestQuestionsResponse(unittest.TestCase):
    """
    note: requires connection to internet
    """
    def test_name_object(self):
        pass
    def test_example_patient(self):
        # read in example json
        json_path = "example_fhir/ex_patient.json"
        curr_pt = read_json_patient(json_path)

        # post to fhir server
        post_url = 'http://fhirtest.uhn.ca/baseDstu3/Patient?_format=json&_pretty=true'
        r = requests.post(post_url, json.dumps(curr_pt.as_json()))

        # assert we got a valid response
        assertTrue(r.ok)

class TestAlexaServer(unittest.TestCase):
    def setUp(self):
        pass

    def test_run_server(self):
        pass

    def test_(self):
        pass

    def tearDown(self):
        pass
if __name__ == "__main__":
    unittest.main()
