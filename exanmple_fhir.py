import json
import fhirclient.models.patient as pt

def create_QuestionnaireResponse():
    pass

path = "example_fhir/ex_patient.json"

with open(path) as data_file:
    data = pt.Patient(json.load(data_file))
