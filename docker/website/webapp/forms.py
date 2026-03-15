"""
Custom Form class for use with flask_wtf
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    org_name = StringField('Organization Name', validators=[DataRequired(), Length(min=2, max=50)])
    org_description = TextAreaField('What does your organization do?', validators=[Length(max=650)])
    it_staff = BooleanField('Does your organization have at least one IT staff member?', validators=[DataRequired()])
    extra_org_info = TextAreaField('Is there anything else you want the clinic to know about your organization?')
    poc_name = StringField('Point Of Contact Name', validators=[DataRequired(), Length(min=2, max=50)])
    poc_title = StringField('Job Title', validators=[DataRequired(), Length(max=50)])
    poc_email = StringField('Email Address', validators=[DataRequired()])
    poc_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10)])
    goals = TextAreaField('What are you looking to achieve through the clinic\'s services?', validators=[Length(max=650)])
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    username = StringField('Username: ', validators=[DataRequired()])
    first_name = StringField('First Name: ', validators=[DataRequired()])
    last_name = StringField('Last Name: ', validators=[DataRequired()])
    email = EmailField('Email: ', validators=[DataRequired(), Email(message="Must be a valid email address")])
    password = PasswordField('Password: ', validators=[DataRequired(), Length(min=15, message="Password must be at least 15 characters long")])
    selection =  SelectField('I am a: ', choices=['client', 'student'], validators=[DataRequired()])
    submit = SubmitField('Submit')