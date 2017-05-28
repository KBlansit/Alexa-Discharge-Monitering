#!/usr/bin/env python

# load libraries
import yaml

# load user defined libraries
from Questionaire import QuestionNode

# define utility functions
def load_questions(path, user):
    # assert that user is either a care_taker or patient
    if user not in ["care_taker", "patient"]:
        raise AssertionError("Must be either a care_taker or patient")

    # load data
    try:
        with open(path, "r") as f:
            data = yaml.load(f)
    except:
        raise IOError("Cannot locate path: " + str(path))

    # define basic queries
    questions = data['application_settings']['master_questerion_ordering']
    question_text = data['application_text']['question_text']
    user = "care_taker"

    # make linked list
    node = None
    for i in questions[::-1]:
        node = QuestionNode(question_text[i][user], child_node=node)

    # return linked list
    return node
