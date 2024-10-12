import requests

from flask import redirect, render_template, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("student_id") is None and session.get("lecturer_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function
