# import libraries
import json
import requests

import fhirclient.models.patient as p

# read in json data
path = "example_fhir/ex_patient.json"
with open(path) as data_file:
    data = json.load(data_file)

# cast as pateint
curr_pt = p.Patient(data)
requests.post(url, json.dumps(data))

url = "http://fhirtest.uhn.ca/baseDstu3/Patient?_format=json&_pretty=true
