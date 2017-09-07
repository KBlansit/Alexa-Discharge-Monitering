#!/usr/bin/env python

# import libraries
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# import user defined libraries
from webapp import create_migration_app

def main():
    """
    main function for migrations
    """
    # create app and db
    app, db = create_app(app_type="MIGRATION")

    # add migrate command
    manager = Manager(app)
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)

    # run manager
    manager.run()

if __name__ == "__main__":
    main()
