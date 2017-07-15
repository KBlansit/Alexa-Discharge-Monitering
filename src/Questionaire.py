#!/usr/bin/env python

# load libraries
import random


class Questionaire:
    """
    the container class to hold administrative and clinical questions
    """
    def __init__(self, clinical_indication, settings_dict):
        """
        INPUTS:
            clinical_indication:
                the clinical indication to
            settings_dict:
                the dictionary that holds the settings
        """
        # save admin questions
        self.admin_questions = settings_dict['application_content']['application_text']['application_questions'].keys()

        # save clinical questions
        self.indication_questions = settings_dict['application_settings']['questions_by_indication']

        # return all clinical questions
        self.all_clinical_questions = settings_dict['application_content']['clinical_questions'].keys()

    def get_admin_question():
        pass

    def get_admin_response():
        pass

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
