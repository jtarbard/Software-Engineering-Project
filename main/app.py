import flask
from flask_qrcode import QRcode

flask_app = flask.Flask(__name__)
QRcode(flask_app)


# All app blueprints are added
def register_blueprints():
    from main.views import index_view
    from main.views import misc_view
    from main.views import info_view
    from main.views import account_view
    from main.views import transaction_view
    from main.views import activities_view

    flask_app.register_blueprint(index_view.blueprint)
    flask_app.register_blueprint(misc_view.blueprint)
    flask_app.register_blueprint(info_view.blueprint)
    flask_app.register_blueprint(account_view.blueprint)
    flask_app.register_blueprint(transaction_view.blueprint)
    flask_app.register_blueprint(activities_view.blueprint)


# Database is setup
def setup_db():
    import main.data.db_session as db_session
    db_session.global_init(flask_app)


# Error logging is created so all errors are recorded
def create_logging():
    import main.logger as logger
    logger.create_transaction_logger()
    logger.create_flask_logger(flask_app)


# App is configured
def configure():
    print("Configuring Flask app:")

    create_logging()
    print("Logging created")

    setup_db()
    print("DB setup completed")

    register_blueprints()
    print("Registered blueprints")

    import main.data.transactions.reset_transaction as rt
    if rt.populate_db(create_timetable=True):
        print("Populated database")
    else:
        print("Database already populated")

    print("Starting application:")


if __name__ == '__main__':
    configure()
    flask_app.run(debug=True)
else:
    configure()
