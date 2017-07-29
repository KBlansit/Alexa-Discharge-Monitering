from src.Questionaire import QuestionContainer

# utility functions and global vars
SETTINGS_PATH = ('resources/application_settings.yaml')
QUESTION_CONTAINER = QuestionContainer(SETTINGS_PATH)

ADMIN_QUESTION_MAP = {
    'PATIENT_CONSENT': 'welcome_text',
    'PATIENT_CONFIRMATION': 'user_identification',
    'PATIENT_2ND_CONFIRMATION': 'user_2nd_step_identification',
}

BASE_SERVICE_REQUEST = "json_fixtures/base_service_request.json"
def construct_session_request_json(intent, session_state, slot=None, question_lst=None):
    """
    INPUTS:
        intent:
            the intent to use
        session_state:
            the session state
        question_lst:
            the question list to add to session attributes
    OUTPUT:
        a dict object which expands a base service request
        note: if question_lst is empty an empty list is constructed
    """
    # may need to remove some of this stuff when sanitizing for HIPPA

    path = BASE_SERVICE_REQUEST

    # read in json file
    with open(path) as data_file:
        body = data_file.read()
        data = json.loads(body)

    # initialize session attributes and set intent and slots
    data['request']['intent'] = {}
    data['request']['intent']['name'] = intent
    data['request']['intent']['slots'] = {}

    # initialize session attributes
    data['session']['attributes'] = {}

    # setting of session_state
    data['session']['attributes']['session_state'] = session_state

    # setting of question_lst with validation
    if question_lst is None:
        data['session']['attributes']['question_lst'] = []
    elif type(question_lst) is list:
        data['session']['attributes']['question_lst'] = question_lst
    else:
        raise AssertionError('question_lst must be list or None')

    # setting of initialized
    data['session']['attributes']['initialized'] = True

    return data
