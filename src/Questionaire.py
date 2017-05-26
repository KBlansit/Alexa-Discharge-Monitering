#!/usr/bin/env python

class QuestionNode:
    def __init__(self):
        # set defaults
        self.children = []
        self.question = None

    # define setter functions
    def add_child_response(self, child_node, response=None):
        """
        INPUTS:
            child_node:
                QuestionNode to be added as a child
        EFFECT:
            sets child_node as a child
        """

        # add child to list
        self.children.append()

    def add_question(self, question):
        """
        INPUTS:
            question:
                the question to add (either string or SSML)
        EFFECT:
            adds child node as a child
        """

        # set question
        self.question = question

    def get_question(self):
        """
        RETURN:
            the question (either string or SSML format)
        """

        return self.question
