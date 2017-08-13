from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Regexp, ValidationError
from tournament.models import User


def validate_email(field):
    if User.exists(field.data):
        raise ValidationError("Email already registered.")


class Register(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(),
                                                     Regexp(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                                            message='Not a valid Email Address'), validate_email])
    name = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
