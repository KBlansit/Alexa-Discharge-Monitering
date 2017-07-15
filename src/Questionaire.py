#!/usr/bin/env python

# load libraries
import random

from flask_ask import statement, question

class Questionaire:
    """
    the container class to hold administrative and clinical questions
    """
    def __init__(self, settings_dict):
        """
        INPUTS:
            settings_dict:
                the dictionary that holds the settings
        EFFECTS:
            sets base attributes for container class
        """
        # save admin information
        self.admin_questions = settings_dict['application_content']['application_text']['application_questions']
        self.admin_statements = settings_dict['application_content']['application_text']['application_statements']

        # save clinical questions
        self.indication_questions = settings_dict['application_settings']['questions_by_indication']

        # return all clinical questions
        self.all_clinical_questions = settings_dict['application_content']['clinical_questions']

    def get_admin_question(question):
        """
        INPUTS:
            question:
                the question to ask
        """
        # test if in dict
        if question not in self.admin_questions.keys():
            raise AssertionError(question + " is not a valid admin question")

        return question(self.admin_questions[question]['text'])

    def get_admin_response(statement):
        """
        INPUTS:
            question:
                the statement o respond with
        """
        # test if in dict
        if statement not in self.admin_statements:
            raise AssertionError(statement + " is not a valid admin statement")

        return statement(self.admin_statements[statement])

    def get_clinical_question():
        pass

    def validate_answer(question, response_type):
        """
        INPUTS:
            question:
                the question we're interested in
            response_type:
                the response type we got back
        """
