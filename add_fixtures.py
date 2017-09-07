#!/usr/bin/env python

# import libraries
import yaml

# import user defined libraries
from src.database import Question, IndicationQuestionOrder
from webapp import create_migration_app

def add_and_commit_fixtures(data, db):
    """
    adds and commits fixture data
    """

    # iterate over clinical conditions
    for condition, content in data['clinical_content'].items():

        # initialize q_dict
        q_dict = {}

        # iterate over each question
        for q, q_info in content['questions'].items():
            # add question to dict
            q_dict[q] = Question(
                q_link_id=q,
                q_text=q_info['text'][0],
                q_type=q_info['response_type'],
            )

        # get order list
        order_list = content['order_list']

        # initialize indication_order_dict and prev_val
        indication_order_dict = {}
        prev_val = None

        # while we still have items in list, process contents
        while len(order_list):
            # pop value
            curr_val = order_list.pop()

            # add to dict as indicationquestionorder
            indication_order_dict[curr_val] = IndicationQuestionOrder(
                indication=condition,
                question=q_dict[curr_val],
            )

            if prev_val:
                indication_order_dict[curr_val].next_item = indication_order_dict[prev_val]

            # increment
            prev_val = curr_val

        # add all to session and commit
        db.session.add_all(q_dict.values())
        db.session.add_all(indication_order_dict.values())

    db.session.commit()

def main():
    # create app and db
    app, db = create_migration_app()

    # read in fixtures
    path = "resources/application_settings.yaml"
    with open(path, "r") as f:
        data = yaml.load(f)

    # call function to add and commit data
    add_and_commit_fixtures(data, db)

if __name__ == "__main__":
    main()
