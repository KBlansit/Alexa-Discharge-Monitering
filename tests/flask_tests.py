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
        Tests that both patient and care_taker can be used for all questions
        """

        # test
        path = "../resources/application_settings.yaml"
        users = ["care_taker", "patient"]
        for i in users:
            load_questions(path, i)

class TestFHIRQuestionnaireResponse(unittest.TestCase):

    def test_positive_control_Questionnaire_response_format(self):
        """
        positive control for validation
        NOTE:
            must be connected to internet
        """
        # define path and get response
        path = 'http://fhirtest.uhn.ca/baseDstu3/QuestionnaireResponse/SMART-PROMs-84-QR5/_history/1?_format=json'
        json_dict = requests.get(path).json()

        # assert that resourceType is valid
        self.assertIn("resourceType", json_dict.keys())
        self.assertEqual(json_dict["resourceType"], "QuestionnaireResponse")

        # assert has id
        self.assertIn("id", json_dict.keys())

        # assert has questionaire reference
        self.assertIn("questionnaire", json_dict.keys())
        self.assertIn("reference", json_dict["questionnaire"])
        self.assertIn("display", json_dict["questionnaire"])

        # assert status is completed
        self.assertIn("status", json_dict.keys())
        self.assertEqual("completed", json_dict["status"])

        # assert linked to patient
        self.assertIn("subject", json_dict.keys())
        self.assertIn("reference", json_dict["subject"])
        self.assertIn("display", json_dict["subject"])

        # assert encounter reference
        self.assertIn("context", json_dict.keys())
        self.assertIn("reference", json_dict["context"])

        # assert that item is valid and populated
        self.assertIn("item", json_dict.keys())
        for i in json_dict["item"]:
            self.assertIn("linkId", i)
            self.assertIn("text", i)
            self.assertIn("answer", i)

if __name__ == "__main__":
    unittest.main()
