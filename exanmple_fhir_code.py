# import libraries
import json
import requests

from fhirclient.models import patient, questionnaireresponse

# example of push data Patient
# read in json data
path = "example_fhir/ex_patient.json"
with open(path) as data_file:
    data = json.load(data_file)

# cast as pateint
curr_pt = patient.Patient(data)

# post to hapi-fhir test server
url = "http://fhirtest.uhn.ca/baseDstu3/Patient?_format=json&_pretty=true"
r = requests.post(url, json.dumps(data))

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

# QuestionnaireResponse
def create_answer(answer_value):
    """
    INPUTS:
        answer_value
            the answer_value to use
    OUTPUT:
        the answer object
    """
    # create answer object
    rslt_answer = questionnaireresponse.QuestionnaireResponseItemAnswer()

    # determine type to create
    curr_type = type(answer_value)
    if curr_type is bool:
        rslt_answer.valueBoolean(answer_value)
    else:
        raise TypeError(str(answer_value) + " is not a valid type")

    return rslt_answer

def create_item_response(linkId, text, answer_lst):
    """
    INPUTS:
        item_name:
            the item name to use
        answer_lst
            the list of items to use
    OUTPUT:
        item object to use
    """
    # create item object
    rslt_item = questionnaireresponse.QuestionnaireResponseItem()
    rslt_item.linkId = linkId

    rslt_item.answer = [create_answer(x) for x in answer_lst]

def create_question_response(answer_dict, completed_status, subject):
    """
    """
