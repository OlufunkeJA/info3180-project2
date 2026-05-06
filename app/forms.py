
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField,
    IntegerField, BooleanField, DateField, FloatField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, NumberRange,
    Optional, ValidationError
)
from datetime import date

# ---------------------------------------------------------------------------
# Like / Pass
# ---------------------------------------------------------------------------
class LikeForm(FlaskForm):
    action = SelectField('Action', choices=[('like', 'Like'), ('pass', 'Pass'), ('dislike', 'Dislike')],
                         validators=[DataRequired()])


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------

class MessageForm(FlaskForm):
    body = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=2000)])


# ---------------------------------------------------------------------------
# Search / Filter
# ---------------------------------------------------------------------------

class SearchForm(FlaskForm):
    q               = StringField('Search',       validators=[Optional()])
    parish          = StringField('Parish',       validators=[Optional()])
    country         = StringField('Country',      validators=[Optional()])
    age_min         = IntegerField('Min Age',     validators=[Optional(), NumberRange(18, 99)])
    age_max         = IntegerField('Max Age',     validators=[Optional(), NumberRange(18, 99)])
    interests       = StringField('Interests',    validators=[Optional()])  # comma-separated
    gender          = SelectField('Gender', choices=[
        ('', 'Any'), ('male', 'Male'), ('female', 'Female'),
        ('non-binary', 'Non-Binary'), ('other', 'Other')
    ], validators=[Optional()])
    sort            = SelectField('Sort By', choices=[
        ('newest', 'Newest'), ('match_score', 'Best Match')
    ], default='newest', validators=[Optional()])