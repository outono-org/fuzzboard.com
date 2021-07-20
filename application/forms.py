from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, ValidationError, HiddenField, PasswordField
from wtforms.fields.core import SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo
from .models import find_user_by_email

STATUS_CHOICES = [('pending', 'Pending'),
                  ("active", "Active"),
                  ("expired", "Expired"),
                  ("rejected", "Rejected")]


class NewJobSubmission(FlaskForm):
    title = StringField("Job title", validators=[DataRequired()])
    company = StringField("Company", validators=[DataRequired()])
    category = SelectField("Category", choices=[
                           ("Pick one"), ("Design"), ("Development"), ("Marketing"), ("Business Development"), ("Other")])
    location = SelectField("Location", choices=[
                           ("Lisboa"), ("Porto"), ("Aveiro"), ("Açores"), ("Beja"), ("Braga"), ("Bragança"), ("Castelo Branco"), ("Coimbra"), ("Évora"), ("Faro"), ("Guarda"), ("Leiria"), ("Madeira"), ("Portalegre"), ("Santarém"), ("Setúbal"), ("Viana do Castelo"), ("Vila Real"), ("Viseu")], validators=[DataRequired()])
    link = StringField("Where should I go to apply?",
                       validators=[DataRequired()])
    email = EmailField("Contact email", validators=[DataRequired(), Email()])
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
