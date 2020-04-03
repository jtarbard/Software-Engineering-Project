import flask
from flask_qrcode import QRcode
from flask_mail import Mail

# All app blueprints are added
def register_blueprints(app):
    from main.views import index_view
    from main.views import misc_view
    from main.views import info_view
    from main.views import account_view
    from main.views import transaction_view
    from main.views import activities_view
    from main.views import basket_view

    app.register_blueprint(index_view.blueprint)
    app.register_blueprint(misc_view.blueprint)
    app.register_blueprint(info_view.blueprint)
    app.register_blueprint(account_view.blueprint)
    app.register_blueprint(transaction_view.blueprint)
    app.register_blueprint(activities_view.blueprint)
    app.register_blueprint(basket_view.blueprint)


# Database is setup
def setup_db(app):
    import main.data.db_session as db_session
    db_session.global_init(app)


# Error logging is created so all errors are recorded
def create_logging(app):
    import main.logger as logger
    logger.create_transaction_logger()
    logger.create_flask_logger(app)


# App is configured
def configure(app):
    print("Configuring Flask app:")

    create_logging(app)
    print("Logging created")

    setup_db(app)
    print("DB setup completed")

    register_blueprints(app)
    print("Registered blueprints")

    import main.data.transactions.reset_transaction as rt
    if rt.populate_db(create_timetable=True, populate_with_random_bookings=True):
        print("Populated database")
    else:
        print("Database already populated")

    print("Configuring error handling pages")

    import main.view_lib.misc_lib as ml

    app.register_error_handler(404, ml.page_not_found)
    app.register_error_handler(405, ml.page_not_found)
    app.register_error_handler(500, ml.page_error)

    print("Defining QRCode integration:")

    QRcode(app)

    print("Starting application:")


# www.patricksoftwareblog.com/structuring-a-flask-project
def create_app(config_filename=None):
    app = flask.Flask(__name__, instance_relative_config=True)
    # app.config.from_pyfile(config_filename)
    # initialize_extensions(app)
    configure(app)
    return app


flask_app = create_app()
flask_app.secret_key = "england is my city"

if __name__ == '__main__':
    flask_app.run(debug=True)

