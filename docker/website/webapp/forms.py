"""
Custom Form class for use with flask_wtf
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    org_name = StringField('Organization Name', validators=[DataRequired(), Length(min=2, max=50)])
    org_description = TextAreaField('What does your organization do?', validators=[Length(max=650)])
    it_staff = BooleanField('Does your organization have at least one IT staff member?', validators=[DataRequired()])
    extra_org_info = TextAreaField('Is there anything else you want the clinic to know about your organization?')
    poc_name = StringField('Point Of Contact Name', validators=[DataRequired(), Length(min=2, max=50)])
    poc_title = StringField('Job Title', validators=[DataRequired(), Length(max=50)])
    poc_email = StringField('Email Address', validators=[DataRequired(), Email()])
    poc_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10)])
    goals = TextAreaField('What are you looking to achieve through the clinic\'s services?', validators=[Length(max=650)])
    submit = SubmitField('Submit')