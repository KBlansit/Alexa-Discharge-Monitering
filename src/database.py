#!/usr/bin/env python

# load libraries
from sqlalchemy import Column, Integer, Date, String, Text, Boolean, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class User(Base):
    __tablename__ = "user"

    # define Base items
    id = Column(Integer, primary_key=True)
    patient_f_name = Column(String(80))
    patient_l_name = Column(String(80))
    patient_bday = Column(Date)
    patient_procedure = Column(String(80))

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

class Question(Base):
    __tablename__ = "question"

    # define Base items
    id = Column(Integer, primary_key=True)
    q_link_id = Column(String(80))
    q_text = Column(Text)
    q_type = Column(String(80))

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

class IndicationQuestionOrder(Base):
    __tablename__ = 'indicationquestionorder'

    # define Base items
    id = Column(Integer, primary_key=True)
    indication = Column(String(80))
    question_id = Column(Integer, ForeignKey(Question.id))
    question = relationship("Question")

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
IndicationQuestionOrder.next_id = Column(Integer, ForeignKey(IndicationQuestionOrder.id))
IndicationQuestionOrder.next_item = relationship(IndicationQuestionOrder, backref = "previous_item", remote_side = IndicationQuestionOrder.id)

class SessionState(Base):
    __tablename__ = "sessionstate"

    # define Base items
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship("User")
    session_id = Column(String(80))
    curr_list_position_id = Column(Integer, ForeignKey(IndicationQuestionOrder.id))
    curr_list_position = relationship("IndicationQuestionOrder")
    session_state = Column(String(80))
    active = Column(Boolean)

    def __init__(
        self,
        user,
        session_id,
        curr_list_position,
    ):
        # from constructor
        self.user = user
        self.session_id = session_id
        self.curr_list_position = curr_list_position # refactor get method to get start from string of indicstion

        # defaults
        self.session_state = 'PATIENT_CONSENT'
        self.active = True

    def __repr__(self):
        return '<Session: {}, State: {}>'.format(self.session_id, self.session_state)

class UserAnswer(Base):
    __tablename__ = "useranswer"

    # define Base items
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship("User")
    question_id = Column(Integer, ForeignKey(Question.id))
    question = relationship("Question")
    answer_bool = Column(Boolean)

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
