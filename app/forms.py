# Add any form classes for Flask-WTF here
from datetime import date
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange, Length, Optional

from app.models import User

class RegistrationForm(FlaskForm):
    
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=80)])
    
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=255)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')])
    
    submit = SubmitField('Register')

def validate_email(form, field):
    # validator to check if email is already registered
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('Email already registered.')

def validate_username(form, field):
    # validator to check if username is already taken
    if User.query.filter_by(username=field.data).first():
        raise ValidationError('Username already taken.')

class LoginForm(FlaskForm):
    class Meta:
        csrf = False  # Disable CSRF for API forms
        
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[Optional(), Length(max=64)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=64)])
    date_of_birth = DateField('Date of Birth', validators=[
        Optional()])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'), 
        ('female', 'Female'),   
        ('non-binary', 'Non-Binary'), 
        ('other', 'Other')], validators=[Optional()])
    looking_for = SelectField('Looking For', choices=[
        ('any', 'Any'), 
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('non-binary', 'Non-Binary')], default='any')   
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])

    parish = StringField('Parish', validators=[Optional(), Length(max=64)])
    city = StringField('City', validators=[Optional(), Length(max=64)])
    country = StringField('Country', validators=[Optional(), Length(max=64)])
    occupation = StringField('Occupation', validators=[Optional(), Length(max=64)])
    education = StringField('Education', validators=[Optional(), Length(max=64)])
    minimum_age = StringField('Minimum Interested Age', validators=[Optional(), NumberRange(min=0)])
    maximum_age = StringField('Maximum Interested Age', validators=[Optional(), NumberRange(min=0)])
    is_pub = SelectField('Public Profile', choices=[
        ('true', 'Yes'),
        ('false', 'No')    ], default='true')
    pfp_accepted = FileField('Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Update Profile')

    def validate_dob(form, field):
        if field.data:
            today = date.today()
            age = today.year - field.data.year - (
                (today.month, today.day) < (field.data.month, field.data.day)
            )
            if age < 18:
                raise ValidationError('You must be at least 18 years or older to register.')

    def validate_min_age(form, field):
        if field.data:
            try:
                age = int(field.data)
                if age < 0 or age < 18 or age > 120:
                    raise ValidationError('Minimum age must be a positive integer and between 18 and 120.')
            except ValueError:
                raise ValidationError('Minimum age must be a valid integer.')
            
    def validate_max_age(form, field):
        if (
            field.data and form.minimum_age.data and 
            field.data.isdigit() and form.minimum_age.data.isdigit()
        ):
            max_age = int(field.data)
            min_age = int(form.minimum_age.data)

            if max_age < min_age:
                raise ValidationError(
                    'Maximum age must be greater than minimum age.'
                )
# Message form for sending messages between users
class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired(), Length(min=1,max=1000)])
    submit = SubmitField('Send')

#Search form for filtering profiles
class SearchForm(FlaskForm):
    age_min = StringField('Minimum Age', validators=[Optional(), NumberRange(min=18, max=120)])
    age_max = StringField('Maximum Age', validators=[Optional(), NumberRange(min=18, max=120
    )])
    gender = SelectField('Gender', choices=[
        ('any', 'Any'), 
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('non-binary', 'Non-Binary')], default='any')
    parish = StringField(
        'Parish',
        validators=[Optional()]
    )

    interests = StringField(
        'Interests',
        validators=[Optional()]
    )

class MessageForm(FlaskForm):

    class Meta:
        csrf = False

    body = TextAreaField(
        'Message',
        validators=[
            DataRequired(),
            Length(min=1, max=2000)
        ]
    )

    submit = SubmitField('Send')