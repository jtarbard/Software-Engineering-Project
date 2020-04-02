# This file is the main driving force for connecting to the
# database by providing a setup for the database as well
# as a connection string and factory return function

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from main.logger import log_server_error

database = SQLAlchemy()


def test_init(flask_app):
    global database

    database.init_app(flask_app)

    import main.data.__all_models
    database.create_all()


# Takes a connection string and sets up a SQLite connection
def global_init(flask_app):
    global database

    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/TheVertex.sqlite'
    database = SQLAlchemy(flask_app)

    import main.data.__all_models
    database.create_all()


def add_to_database(database_class):
    try:
        database.session.add(database_class)
        database.session.commit()
        return True
    except SQLAlchemyError as e:
        log_server_error(str(e))
        return False


def delete_from_database(database_class):
    try:
        database.session.delete(database_class)
        database.session.commit()
        return True
    except SQLAlchemyError as e:
        log_server_error(str(e))
        return False
