# https://stackoverflow.com/questions/23987564/test-flask-render-template-context
from flask import template_rendered, message_flashed
from contextlib import contextmanager


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


# Testing messages are flashed
@contextmanager
def captured_flashes(app):
    recorded = []

    def record(sender, message, category, **extra):
        recorded.append((message, category))

    message_flashed.connect(record, app)
    try:
        yield recorded
    finally:
        message_flashed.disconnect(record, app)
