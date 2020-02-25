from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from main.logger import log_server_error

database = None
session = None


# Takes a connection string and sets up a SQLite connection
def global_init(flask_app):
    global database, session

    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/TheVertex.sqlite'
    database = SQLAlchemy(flask_app)
    session = database.session

    import main.data.__all_models
    database.create_all()


def add_to_database(database_class):
    try:
        session.add(database_class)
        session.commit()
        return True
    except SQLAlchemyError as e:
        log_server_error(str(e))
        return False