import logging

LOG_FORMAT = "%(asctime)s:%(name)s:%(message)s"

transaction_logger = None
server_logger = None


def create_transaction_logger():
    transaction_handler = logging.FileHandler("logs/transactions.log")
    transaction_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    global transaction_logger
    transaction_logger = logging.getLogger(__name__)
    transaction_logger.setLevel(logging.INFO)
    transaction_logger.addHandler(transaction_handler)


def create_flask_logger(flask_app):
    server_error_handler = logging.FileHandler("logs/server_error.log")
    server_error_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    server_error_handler.setLevel(logging.WARNING)

    global server_logger
    flask_app.logger.addHandler(server_error_handler)
    server_logger = flask_app.logger


def log_transaction(message):
    transaction_logger.info(message)


def log_server_error(message):
    server_logger.error(message)
