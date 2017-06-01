#!/usr/bin/env python

# load libraries
import sys
import json
import yaml
import unittest
import requests

# go up a directory to see project root dir
sys.path.append("..")

# load user defined libraries
from src.utilities import load_questions
from src.fhir_validators import validate_encounter, validate_example_questionnaire,\
    validate_example_questionnaire_response

class TestQuestionsStructure(unittest.TestCase):

    def test_question_list_valid(self):
        """
        Tests that list of questions is valid
        """

        # load data
        path = "../resources/application_settings.yaml"
        try:
            with open(path, "r") as f:
                data = yaml.load(f)
        except IOError:
            raise IOError("Cannot locate path: " + str(path))

        # define basic queries
        questions = data['application_settings']['master_questerion_ordering']
        question_text = data['application_text']['question_text']

        for i in questions:
            self.assertIn(i, question_text.keys())

    def test_question_loader(self):
        """
        Tests that both patient and caretaker can be used for all questions
        """
        LIST_OF_QS = [
            "person_confirmation",
            "moving_question",
            "eating_question",
            "drinking_question",
            "pain_control_question",
        ]

        # test
        path = "../resources/application_settings.yaml"
        users = ["caretaker", "patient"]

        # load data
        try:
            with open(path, "r") as f:
                data = yaml.load(f)
        except IOError:
            raise IOError("Cannot locate path: " + str(path))

        for i in users:
            load_questions(data, i, LIST_OF_QS)

class TestFHIRStructure(unittest.TestCase):

    def test_positive_control_Questionnaire_Response_format(self):
        """
        positive control for validation
        NOTE:
            must be connected to internet
        """
        # open file
        with open('example_fhir/example_Questionnaire_Response.json', 'r') as f:
            data = json.load(f)

        # run through validator
        validate_example_questionnaire_response(data)


    def test_positive_control_Questionnaire_format(self):
        """
        positive control for validation
        NOTE:
            must be connected to internet
        """
        # open file
        with open('example_fhir/example_Questionnaire.json', 'r') as f:
            data = json.load(f)

        # run through validator
        validate_example_questionnaire(data)

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
