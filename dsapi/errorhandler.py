from flask import jsonify
from werkzeug.exceptions import HTTPException, default_exceptions


def json_errorhandler(exception):
    """Generate a JSON-encoded Flask response for an exception."""

    if isinstance(exception, HTTPException):
        message = exception.description
        code = exception.code
    else:
        message = 'Internal server error'
        code = 500

    response = jsonify({
        'message': message,
        'error': True
    })
    response.status_code = code

    return response


def register(app):
    """Register a JSON error handler for all HTTP exceptions on a Flask app.

    Parameters
    ----------
    app : flask.Flask
        The Flask app to configure
    """
    for code in default_exceptions.keys():
        app.register_error_handler(code, json_errorhandler)
