from flask import session, url_for, redirect
from functools import wraps


def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect(url_for('auth.login'))
        return function(*args, **kwargs)
    return decorated_function
