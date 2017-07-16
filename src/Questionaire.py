#!/usr/bin/env python

# load libraries
import random

from flask_ask import statement, question
from src.utilities import load_settings_and_content

class Questionaire:
    """
    the container class to hold administrative and clinical questions
    """
    def __init__(self, settings_path):
        """
        INPUTS:
            settings_dict:
                the dictionary that holds the settings
        EFFECTS:
            sets base attributes for container class
        """
        settings_dict = load_settings_and_content(settings_path)

        # save admin information
        self.admin_questions = settings_dict['application_content']['application_text']['application_questions']
        self.admin_statements = settings_dict['application_content']['application_text']['application_statements']

        # save clinical questions
        self.indication_questions = settings_dict['application_settings']['questions_by_indication']

        # return all clinical questions
        self.all_clinical_questions = settings_dict['application_content']['clinical_questions']

    def get_admin_question(self, question):
        """
        INPUTS:
            question:
                the question to ask
        OUTPUT:
            a (str) question with the apprioprate text
        """
        # test if in dict
        if question not in self.admin_questions.keys():
            raise AssertionError(question + " is not a valid admin question")

        return self.admin_questions[question]['text']

    def get_admin_response(self, statement):
        """
        INPUTS:
            statement:
                the statement to respond with
        OUTPUT:
            a (str) statement with the apprioprate text
        """
        # test if in dict
        if statement not in self.admin_statements:
            raise AssertionError(statement + " is not a valid admin statement")

        return self.admin_statements[statement]

    def get_list_of_clinical_questions(self, clinical_indication):
        """
        INPUTS:
            clinical_indication:
                the clinical indication to get questions for
        OUTPUT:
            a list of question keys for a given indication
        """
        # test if in dict
        if clinical_indication not in self.indication_questions.keys():
            raise AssertionError(clinical_indication + " is not a valid clinical indication")

        return self.indication_questions[clinical_indication]

    def get_clinical_questions(self, question):
        """
        INPUTS:
            question:
                the question to ask
        OUTPUT:
            a (str) question with the apprioprate text
        """
        # test if in dict
        if question not in self.all_clinical_questions.keys():
            raise AssertionError(question + " is not a valid clinical question")

        return self.all_clinical_questions[question]['text']

    def validate_answer(self, question, response_type):
        """
        INPUTS:
            question:
                the question we're interested in
            response_type:
                the response type we got back
        OUTPUT:
            Bool is the response type is apprioprate
        """
        # test if in dict
        if question not in self.all_clinical_questions.keys():
            raise AssertionError(question + " is not a valid clinical question")

        if response_type is not self.all_clinical_questions[question]['response_type']:
            raise AssertionError(question + " does not have a " + response_type + " response")
