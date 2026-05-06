from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import DateField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, ValidationError

from app.models import Account


class RegistrationForm(FlaskForm):
    handle = StringField("Handle", validators=[DataRequired(), Length(min=2, max=64)])
    email_address = StringField("Email Address", validators=[DataRequired(), Email(), Length(max=128)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=255)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )

    submit = SubmitField("Register")

    def validate_email_address(self, field):
        if Account.query.filter_by(email_address=field.data.lower().strip()).first():
            raise ValidationError("Email already registered.")

    def validate_handle(self, field):
        if Account.query.filter_by(handle=field.data.strip()).first():
            raise ValidationError("Handle already taken.")


class LoginForm(FlaskForm):
    email_address = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ProfileForm(FlaskForm):
    first_name = StringField("First Name", validators=[Optional(), Length(max=64)])
    surname = StringField("Surname", validators=[Optional(), Length(max=64)])
    birthdate = DateField("Birthdate", validators=[Optional()])
    gender = SelectField(
        "Gender",
        choices=[("male", "Male"), ("female", "Female"), ("non-binary", "Non-Binary"), ("other", "Other")],
        validators=[Optional()],
    )
    seeking = SelectField(
        "Seeking",
        choices=[("any", "Any"), ("male", "Male"), ("female", "Female"), ("non-binary", "Non-Binary")],
        default="any",
    )
    about_me = TextAreaField("About Me", validators=[Optional(), Length(max=500)])

    parish = StringField("Parish", validators=[Optional(), Length(max=64)])
    city = StringField("City", validators=[Optional(), Length(max=64)])
    country = StringField("Country", validators=[Optional(), Length(max=64)])
    job_title = StringField("Job Title", validators=[Optional(), Length(max=128)])
    schooling = StringField("Schooling", validators=[Optional(), Length(max=64)])
    min_age = IntegerField("Minimum Interested Age", validators=[Optional(), NumberRange(min=18, max=99)])
    max_age = IntegerField("Maximum Interested Age", validators=[Optional(), NumberRange(min=18, max=99)])
    visible = SelectField("Visible Profile", choices=[("true", "Yes"), ("false", "No")], default="true")

    avatar_file = FileField("Profile Picture", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png"], "Images only!")])
    submit = SubmitField("Update Profile")


class ChatMessageForm(FlaskForm):
    content = TextAreaField("Message", validators=[DataRequired(), Length(min=1, max=2000)])
    submit = SubmitField("Send")


class SearchForm(FlaskForm):
    age_min = IntegerField("Minimum Age", validators=[Optional(), NumberRange(min=18, max=120)])
    age_max = IntegerField("Maximum Age", validators=[Optional(), NumberRange(min=18, max=120)])
    gender = SelectField(
        "Gender",
        choices=[("any", "Any"), ("male", "Male"), ("female", "Female"), ("non-binary", "Non-Binary")],
        default="any",
    )
    parish = StringField("Parish", validators=[Optional()])
    interests = StringField("Interests", validators=[Optional()])


class SwipeForm(FlaskForm):
    action = SelectField("Action", choices=[("yes", "Yes"), ("pass", "Pass"), ("no", "No")], validators=[DataRequired()])
