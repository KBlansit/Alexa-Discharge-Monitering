#!/usr/bin/env python

# load libraries
import unittest

# load user defined libraries
from src.utilities import load_questions

class TestQuestionsStructure(unittest.TestCase):

    def test_question_loader(self):
        """
        Tests that both patient and care_taker can be used for all questions
        """

        # test
        path = "resources/application_text.yaml"
        users = ["care_taker", "patient"]
        for i in users:
            self.questions = load_questions(path, i)

if __name__ == "__main__":
    unittest.main()
