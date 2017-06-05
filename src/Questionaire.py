#!/usr/bin/env python

# load libraries
import random

class QuestionNode:
    def __init__(self, question_lst=None, child_node=None, name=None):

        # set parameters
        self.question_lst = question_lst
        self.child_node = child_node
        self.name = name

    def to_list(self):
        """
        transforms the linked list into a flat list and chooses questions
        """

        # use to bootstrap vars
        rslt_lst = []
        curr_node = self

        # iterate until there no children left
        while curr_node.child_node is not None:
            # add question to list
            rslt_lst.append(random.choice(curr_node.question_lst))

            # update node
            curr_node = curr_node.child_node

        return rslt_lst[::-1]

    def __str__(self):
        return name
