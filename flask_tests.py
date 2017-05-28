#!/usr/bin/env python

# load libraries
import yaml
import unittest
from itertools import product

# load user defined libraries
from src.Questionaire import QuestionNode

class TestQuestionsStructure(unittest.TestCase):

    def setUp(self):
        path = "resources/application_text.yaml"
        try:
            with open(path, "r") as f:
                self.data = yaml.load(f)
        except:
            raise IOError("Cannot locate path: " + str(path))

    def test_question_loader(self):

        # define basic queries
        questions = self.data['application_settings']['master_questerion_ordering']
        question_text = self.data['application_text']['question_text']
        user = "care_taker"

        # make linked list
        prev_node = None
        for i in questions[::-1]:
            prev_node = QuestionNode(question_text[i][user], child_node=prev_node)

if __name__ == "__main__":
    unittest.main()
