#!/usr/bin/env python

# import libraries
import yaml
import argparse

# import user defined libraries
from webapp import create_test_app, create_production_app
from add_fixtures import add_and_commit_fixtures

def choose_run_type(cmd_args):
    """
    function to help determine which type of function to use
    """
    if cmd_args.postgresql:
        # create app and db
        app, db = create_production_app()

        # return app and db
        return app, db
    else:
        # create app and db
        app, db = create_test_app()

        # create tables
        db.create_all()

        # read in fixtures
        path = "resources/application_settings.yaml"
        with open(path, "r") as f:
            data = yaml.load(f)

        # add data to database
        add_and_commit_fixtures(data, db)

        # return app and db
        return app, db

def main():
    """
    script to launch a synthetic test server
    """
    # parse command line args
    cmd_parse = argparse.ArgumentParser(description = 'Application for testing app in pseudo-production enviorment')
    cmd_parse.add_argument('-p', '--postgresql', help = 'tests against specified postgresql', type=str)
    cmd_args = cmd_parse.parse_args()

    # create app and db
    app, db = choose_run_type(cmd_args)

    # run app
    app.run()

if __name__ == '__main__':
    main()
