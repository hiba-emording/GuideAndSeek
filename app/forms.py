#!/usr/bin/python3
"""Flask Forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, PasswordField, SubmitField, EmailField, TextAreaField, TimeField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange
from wtforms.widgets import ListWidget, CheckboxInput
import pytz
from pytz import timezone


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=2, max=20, message="Username must be between 2 and 20 characters.")
    ])
    email = EmailField('Email', validators=[
        DataRequired(message="Email is required."),
        Email(message="Please provide a valid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Password confirmation is required."),
        EqualTo('password', message="Passwords must match.")
    ])
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')
    

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ProfileEditForm(FlaskForm):
    bio = StringField('Bio', validators=[Length(max=500)])
    profile_picture = StringField('Profile Picture URL', validators=[Optional(), Length(max=255)])
    
    # Select a country
    country = SelectField('Country', validators=[Optional()], coerce=str)
    timezone = SelectField('Timezone', choices=[(tz, tz) for tz in pytz.all_timezones])
    # Level dropdown for education levels
    level = SelectField('Level', choices=[
        ('', 'All'),
        ('Primary School', 'Primary School'),
        ('High School', 'High School'),
        ('College', 'College'),
        ('Postgraduate', 'Postgraduate')
    ], validators=[Optional()])
    
    # Multiple subject selection
    subject = SelectMultipleField('Subjects of Interest', validators=[Optional()], 
                                  widget=ListWidget(prefix_label=False), 
                                  option_widget=CheckboxInput())
    
    submit = SubmitField('Save Changes')

class AvailabilityForm(FlaskForm):
    day_of_week = SelectField('Day of the Week', choices=[('Monday', 'Monday'),
                 ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
                 ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),
                 ('Sunday', 'Sunday')],validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    submit = SubmitField('Set Availability')


class AppointmentForm(FlaskForm):
    title = StringField('Session Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    material_url = StringField('Material URL (optional)')
    slot_time = SelectField('Available Slots', choices=[])
    google_meet_link = StringField('Session Link', validators=[DataRequired()])
    submit = SubmitField('Request Appointment')



class ReviewForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[
        DataRequired(), 
        NumberRange(min=1, max=5, message='Rating must be between 1 and 5.')
    ])
    comment = TextAreaField('Comment (optional)')
    submit = SubmitField('Submit Review')
