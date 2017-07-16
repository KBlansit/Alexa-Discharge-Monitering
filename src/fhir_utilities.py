#!/usr/bin/env python

# import libraries
import json

from fhirclient.models import patient, questionnaireresponse
from fhirclient.models.fhirreference import FHIRReference
from fhirclient.models.fhirdate import FHIRDate

def read_json_patient(path):
    """
    INPUTS:
        path:
            path to example json file
    OUTPUT:
        the patient object
    """
    with open(path) as data_file:
        return patient.Patient(json.load(data_file))

def create_item(linkId, answer_value):
    """
    INPUTS:
        linkId:
            the linkId for the answer
        answer_value:
            the answer value (limited here to only a single value)
    OUTPUT:
        item object to use
    """
    # create item object
    rslt_item = questionnaireresponse.QuestionnaireResponseItem()

    # creat answer object
    rslt_answer = questionnaireresponse.QuestionnaireResponseItemAnswer()

    # determine type to create
    curr_type = type(answer_value)
    if curr_type is bool:
        rslt_answer.valueBoolean = answer_value
    elif curr_type in [list, tuple, dict]:
        raise AssertionError("list, tuple, and dict types are not supported now")
    else:
        raise TypeError(str(answer_value) + " is not a valid type")

    # add data to rslt_item object
    rslt_item.linkId = linkId
    rslt_item.answer = [rslt_answer]

    # validate that we can cast as json and return
    assert rslt_answer.as_json()
    assert rslt_item.as_json()

    return rslt_item

def create_patient_reference(patient):
    rslt_rf = FHIRReference()
    rslt_rf.display = patient.name[0].text

    # validate that we can cast as json and return
    assert rslt_rf.as_json()

    return rslt_rf


def create_question_response(answer_dict, completed_status, subject):
    """
    INPUTS:
        answer_dict:
            the dictionary of answers to create
        completed_status:
            the status of the questionaire
        subject:
            the subject who'se performing this
    OUTPUT:
        a formatted QuestionnaireResponse object
    """
    # create QuestionnaireResponse object
    rslt_qr = questionnaireresponse.QuestionnaireResponse()

    # iterate over dictionary
    answer_item_lst = [create_item(k, v) for k, v in answer_dict.items()]

    # add data to to rslt_qr
    rslt_qr.status = completed_status
    rslt_qr.item = answer_item_lst
    rslt_qr.subject = create_patient_reference(subject)

    # validate that we can cast as json and return
    assert rslt_qr.as_json()

    return rslt_qr
