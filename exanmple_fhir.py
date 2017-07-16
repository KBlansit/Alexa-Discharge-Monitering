# import libraries
import json
import requests

import fhirclient.models.patient as p

# read in json data
path = "example_fhir/ex_patient.json"
with open(path) as data_file:
    data = json.load(data_file)
p.Patient(data)
