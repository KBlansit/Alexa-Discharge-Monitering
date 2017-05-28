#!/usr/bin/env python

class QuestionNode:
    def __init__(self, question=None, child_node=None):
        # set either parameters or defaults
        if question is None:
            self.question = None
        else:
            self.question = question

        if child_node is None:
            self.child = None
        else:
            self.child = child_node

    def __str__(self):
        if type(self.question) == list:
            for i in self.question:
                return i + "\n"
            else:
                return self.question
