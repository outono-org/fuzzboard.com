from flask import session, url_for, redirect
from functools import wraps
from .database import mongo


def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect(url_for('auth.login'))
        return function(*args, **kwargs)
    return decorated_function


def admin_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        user = mongo.db.users.find_one_or_404({'email': session["username"]})
        if user["user_type"] != ("admin" and "super_admin"):
            return redirect(url_for('main.home'))
        return function(*args, **kwargs)
    return decorated_function
