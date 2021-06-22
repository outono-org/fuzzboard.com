from flask_mail import Mail, Message
from flask.templating import render_template

mail = Mail()


def send_email(subject, to, template, job_title, company):
    msg = Message(subject, recipients=[to])
    msg.body = render_template(
        template + ".html", job_title=job_title, company=company)
    msg.html = render_template(
        template + ".html", job_title=job_title, company=company)
    mail.send(msg)
