from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, ValidationError
from wtforms.fields.core import SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo


class NewJobSubmission(FlaskForm):
    title = StringField("Job title", validators=[DataRequired()])
    company = StringField("Company", validators=[DataRequired()])
    category = SelectField("Category", choices=[
                           ("Pick one"), ("Design"), ("Development"), ("Marketing"), ("Business Development"), ("Other")])
    location = StringField("Location", validators=[DataRequired()])
    link = StringField("Where should I go to apply?",
                       validators=[DataRequired()])
    email = EmailField("Contact email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit job")
