from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, TextAreaField, ValidationError, HiddenField, PasswordField
from wtforms.fields.core import SelectField, BooleanField
from wtforms.widgets import TextArea
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, URL
from flask_mde import Mde, MdeField
from .models import find_user_by_email

STATUS_CHOICES = [('pending', 'Pending'),
                  ("active", "Active"),
                  ("expired", "Expired"),
                  ("rejected", "Rejected")]


class NewJobSubmission(FlaskForm):
    title = StringField("Job title", validators=[DataRequired()])
    company = StringField("Company", validators=[DataRequired()])
    category = SelectField("Category", choices=[
                           ("Pick one"), ("Design"), ("Development"), ("Marketing"), ("Product Management"), ("Business Development"), ("Other")])
    location = SelectField("Location", choices=[
                           ("Remote"), ("Lisboa"), ("Porto"), ("Aveiro"), ("Açores"), ("Beja"), ("Braga"), ("Bragança"), ("Castelo Branco"), ("Coimbra"), ("Évora"), ("Faro"), ("Guarda"), ("Leiria"), ("Madeira"), ("Portalegre"), ("Santarém"), ("Setúbal"), ("Viana do Castelo"), ("Vila Real"), ("Viseu")], validators=[DataRequired()])
    description = StringField(u'Description', widget=TextArea())
    link = StringField("Where should I go to apply?",
                       validators=[DataRequired(), URL()])
    email = EmailField("Contact email", validators=[DataRequired(), Email()])
    visa_sponsor = BooleanField(
        label="🇺🇦 We're willing to sponsor a Ukrainian citizen escaping the country along with their family.")
    submit = SubmitField("Submit job")


class JobManagement(FlaskForm):
    status = SelectField(u'Status', choices=STATUS_CHOICES)
    id = HiddenField("id")
    save = SubmitField("Save")


class RefreshJobStatus(FlaskForm):
    button = SubmitField("Refresh")

# Authentication


class SignIn(FlaskForm):
    email_address = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password")
    submit = SubmitField("Login")


class SignUp(FlaskForm):
    email_address = EmailField("Email", validators=[DataRequired(), Email()])
    name = StringField("Name", validators=([DataRequired()]))
    password = PasswordField("Password", validators=[DataRequired(), EqualTo(
        "password2", message="Passwords must match.")])
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Create Account")

    def validate_email_address(self, field):
        email_address = field.data
        if find_user_by_email(email=email_address):
            #flash("Email already registered.")
            raise ValidationError('Email already registered.')


class NewsletterSubscribe(FlaskForm):
    MERGE0 = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Keep me posted")


class StartupsTestForm(FlaskForm):
    feedback = TextAreaField("Tell us why this is important to you")
    email = EmailField("Email*", validators=[DataRequired(), Email()])
    submit = SubmitField("Keep me posted")


class UploadPicture(FlaskForm):
    file = FileField(validators=[FileRequired()])
    submit = SubmitField("Upload new picture")
