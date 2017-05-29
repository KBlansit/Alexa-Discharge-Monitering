#!/usr/bin/env python

# load libraries
import yaml

# load user defined libraries
from Questionaire import QuestionNode

# define utility functions
def load_questions(data, user, curr_questions):
    # assert that user is either a care_taker or patient
    if user not in ["care_taker", "patient"]:
        raise AssertionError("Must be either a care_taker or patient")

    # define basic queries
    questions = data['application_settings']['master_questerion_ordering']
    question_text = data['application_text']['question_text']

    # make linked list
    node = None
    for i in questions[::-1]:
        node = QuestionNode(question_text[i][user], child_node=node)

    # return linked list
    return node.to_list(curr_questions)

def critical_questions(data, curr_questions):
    crit_lst = data['application_settings']['hard_assertion_questions']
    return list(set(curr_questions) & set(crit_lst))
