#!/usr/bin/env python

# load libraries
import sys
import json
import yaml
import unittest
import requests

# load user defined libraries
from src.utilities import load_settings_and_content, load_questions, extract_questionnaire_questions
from src.fhir_validators import validate_encounter, validate_example_questionnaire,\
    validate_example_questionnaire_response

class TestQuestionsStructure(unittest.TestCase):

    def test_load_content_and_settings(self):
        """
        Tests that can load the content and settings yaml file
        """
        # load data
        path = "resources/application_settings.yaml"
        settings = load_settings_and_content(path)

        # define basic queries
        procedure_questions = settings['application_settings']['question_lists']
        question_text = settings['application_content']['question_text']

        for p in procedure_questions.keys():
            for q in procedure_questions[p]:
                self.assertIn(q, question_text.keys())

    def test_question_loader(self):
        """
        tests that question loader function works
        """
        # load data
        path = "resources/application_settings.yaml"
        settings = load_settings_and_content(path)

        # load question into container class
        load_questions(settings, 'ileostomy')

class TestFHIRStructure(unittest.TestCase):

    def test_positive_control_Questionnaire_Response_format(self):
        """
        positive control for QuestionnaireResponse
        """
        # open file
        path = 'example_fhir/example_Questionnaire_Response.json'
        with open(path, 'r') as f:
            data = json.load(f)

        # run through validator
        validate_example_questionnaire_response(data)

    def test_positive_control_Questionnaire_format(self):
        """
        positive control for Questionnaire
        """
        # open file
        path = 'example_fhir/example_Questionnaire.json'
        with open(path, 'r') as f:
            data = json.load(f)

        # run through validator
        validate_example_questionnaire(data)

    def test_positive_control_Encounter_format(self):
        """
        positive control for Questionnaire
        """
        # open file
        path = 'example_fhir/example_Encounter.json'
        with open(path, 'r') as f:
            data = json.load(f)

        # run through validator
        validate_encounter(data)

    def test_Questionnaire_JSON(self):
        """
        control for QuestionnaireResponse
        """
        # open file
        path = 'resources/example_FHIR_resources/example_questionnaire.json'
        with open(path, 'r') as f:
            data = json.load(f)

        # run through validator
        validate_example_questionnaire(data)

        # extract questions
        extract_questionnaire_questions(data)

        LIST_OF_QS = [
            "Person Confirmation",
            "Mobility",
            "Currently Eating",
            "Currently Drinking",
            "Currently Taking Pain Medications",
        ]

        # assert same
        self.assertItemsEqual(extract_questionnaire_questions(data), LIST_OF_QS)


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
