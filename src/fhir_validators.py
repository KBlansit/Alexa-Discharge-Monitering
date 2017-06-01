#!/usr/bin/env python

def validate_example_questionnaire(data):
    """
    validates json data to questionnaire
    """
    # validate that resourceType is valid
    assert "resourceType" in data.keys()
    assert data["resourceType"] in "Questionnaire"

    # validate has id
    assert "id" in data.keys()

    # validate has identifer
    assert "identifier" in data.keys()
    assert "system" in data["identifier"][0].keys()
    assert "use" in data["identifier"][0].keys()

    # validate that item is valid and populated
    assert "item" in data.keys()
    for i in data["item"]:
        assert "linkId" in i
        assert "text" in i
        assert "type" in i
        assert "options" in i

def validate_example_questionnaire_response(data):
    """
    validates json data to questionnaire
    """
    # validate resource type
    assert "resourceType" in data.keys()
    assert data["resourceType"] == "QuestionnaireResponse"

    # validate has id
    assert "id" in data.keys()

    # validate has questionaire reference
    assert "questionnaire" in data.keys()
    assert "reference" in data["questionnaire"]
    assert "display" in data["questionnaire"]

    # validate status is completed
    assert "status" in data.keys()
    assert "completed" in data["status"]

    # validate linked to patient
    assert "subject" in data.keys()
    assert "reference" in data["subject"]
    assert "display" in data["subject"]

    # validate ncounter reference
    assert "context" in data.keys()
    assert "reference" in data["context"]

    # validate that item is valid and populated
    assert "item" in data.keys()
    for i in data["item"]:
        assert "linkId" in i
        assert "text" in i
        assert "answer" in i

def validate_encounter(data):
    """
    validates json data to questionnaire
    """
