#!/usr/bin/env python

# load libraries
import yaml

# load user defined libraries
from Questionaire import QuestionNode

def load_settings_and_content(settings_path):
    """
    INPUTS:
        settings_path:
            the path to the yaml settings and content file
    OUTPUT:
        the dictionary of the settings data
    """
    # load data
    try:
        with open(settings_path, "r") as f:
            data = yaml.load(f)
    except IOError:
        raise IOError("Cannot locate path: " + str(path))

    return data

def load_questions(data, procedure):
    """
    INPUTS:
        data:
            the dictionary setting and content file
        procedure:
            a string that defines the key of the setting file for the current procedure
    OUTPUT:
        a list of questions to ask
    """
    # define basic queries
    questions = data['application_settings']['question_lists'][procedure]
    question_text = data['application_content']['question_text']

    # make linked list
    node = None
    for i in questions[::-1]:
        node = QuestionNode(question_text[i], child_node=node)

    # return linked list
    return node.to_list()

def extract_questionnaire_questions(data):
    """
    extracts a list of questions from questionnaire data
    """
    # make list
    question_lst = []

    # extract information
    for i in data['item']:
        question_lst.append(i['linkId'])

    # make literal
    question_lst = [str(item) for item in question_lst]

    return question_lst
