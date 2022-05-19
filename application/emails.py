import os
from flask_mail import Mail, Message
from flask.templating import render_template
from .database import mongo
from .models import get_reset_password_token, find_user_by_email

mail = Mail()


def send_email(subject, to, template, job_title=None, company=None, token: str = None):
    msg = Message(subject, recipients=[to])
    msg.body = render_template(
        template + ".html", job_title=job_title, company=company, token=token)
    msg.html = render_template(
        template + ".html", job_title=job_title, company=company, token=token)
    mail.send(msg)


def send_password_reset_email(email: str):
    # ERROR: Object of type ObjectId is not JSON serializable.
    # I'm turning the objectID into a string. Is this a problem?
    user = find_user_by_email(email=email)
    token = get_reset_password_token(user_id=str(user['_id']))
    send_email(subject='Fuzzboard: Reset your password',
               to=email,
               template='mail/reset_password', token=token)
