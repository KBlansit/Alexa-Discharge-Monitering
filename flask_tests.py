#!/usr/bin/env python

# load libraries
import yaml
import unittest

# load user defined libraries
from src.Questionaire import QuestionNode

class TestQuestionsStructure(unittest.TestCase):

    def setUp(self):
        path = 'resources/application_text.yaml'
        try:
            with open(path, "r") as f:
                self.data = yaml.load(f)
        except:
            raise IOError("Cannot locate path: " + str(path))

    def test_question_loader(self):
        import pdb; pdb.set_trace()
        
        pass

if __name__ == '__main__':
    unittest.main()
