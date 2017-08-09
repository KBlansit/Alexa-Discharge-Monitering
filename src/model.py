#!/usr/bin/env python

# load libraries
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    # define model items
    id = db.Column(db.Integer, primary_key=True)
    patient_f_name = db.Column(db.String(80))
    patient_l_name = db.Column(db.String(80))
    patient_bday = db.Column(db.Date)
    patient_procedure = db.Column(db.String(80))

    def __init__(
        self,
        patient_f_name,
        patient_l_name,
        patient_bday,
        patient_procedure,
    ):
        self.patient_f_name = patient_f_name
        self.patient_l_name = patient_l_name
        self.patient_bday = patient_bday
        self.patient_procedure = patient_procedure

    def __repr__(self):
        return '<User: {} {}>'.format(self.patient_f_name, self.patient_l_name)

class Question(db.Model):
    # define model items
    id = db.Column(db.Integer, primary_key=True)
    q_link_id = db.Column(db.String(80))
    q_text = db.Column(db.Text)
    q_type = db.Column(db.String(80))

    def __init__(
        self,
        q_link_id,
        q_text,
        q_type,
    ):
        self.q_link_id = q_link_id
        self.q_text = q_text

    def __repr__(self):
        return '<QuestionID: {}>'.format(self.q_link_id)

class IndicationQuestionOrder(db.Model):
    __tablename__ = 'indicationquestionorder'

    # define model items
    id = db.Column(db.Integer, primary_key=True)
    indication = db.Column(db.String(80))
    question_id = db.Column(db.Integer, db.ForeignKey(Question.id))
    question = db.relationship("Question")

    def __init__(
        self,
        indication,
        next_item,
        question,
    ):
        self.indication = indication
        self.next_item = next_item
        self.question = question

    def __repr__(self):
        return '<Indication: {}, Question: {}>'.format(self.indication, self.question)

# monkey patch
IndicationQuestionOrder.next_id = db.Column(db.Integer, db.ForeignKey(IndicationQuestionOrder.id))
IndicationQuestionOrder.next_item = db.relationship(IndicationQuestionOrder, backref = "previous_item", remote_side = IndicationQuestionOrder.id)

class SessionState(db.Model):
    # define model items
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship("User")
    session_id = db.Column(db.String(80))
    curr_list_position_id = db.Column(db.Integer, db.ForeignKey(IndicationQuestionOrder.id))
    curr_list_position = db.relationship("IndicationQuestionOrder")

    session_state = db.Column(db.String(80))
    active = db.Column(db.Boolean)

    def __init__(
        user,
        session_id,
        curr_list_position,
    ):
        # from constructor
        self.user = user
        self.session_id = session_id
        self.curr_list_position = curr_list_position

        # defaults
        self.session_state = 'PATIENT_CONSENT'
        self.active = True

    def __repr__(self):
        return '<Session: {}, State: {}>'.format(self.session_id, self.session_state)

class UserAnswer(db.Model):
    # define model items
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship("User")
    question_id = db.Column(db.Integer, db.ForeignKey(Question.id))
    question = db.relationship("Question")
    answer_bool = db.Column(db.Boolean)

    def __init__(
        self,
        user,
        question,
        answer_bool = None,
    ):
        self.user = user
        self.question = question
        self.answer_bool = answer_bool

    def __repr__(self):
        return '<User: {}, Answer: {}>'.format(self.user, self.answer_bool)
