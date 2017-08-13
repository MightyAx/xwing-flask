import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Regexp, ValidationError
from tournament.models import User


class EmailUnregistered(object):
    def __init__(self, message=None):
        if not message:
            message = "Email already registered."
        self.message = message

    def __call__(self, form, field):
        if User.exists(field.data):
            raise ValidationError(self.message)


class Register(FlaskForm):
    email = StringField('Email Address',
                        validators=[
                            DataRequired(),
                            Regexp(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                   message='Not a valid Email Address.'),
                            EmailUnregistered(message="Email already registered.")
                        ])
    name = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class Login(FlaskForm):
    email = StringField('Email Address',
                        validators=[
                            DataRequired(),
                            Regexp(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                   message='Not a valid Email Address.')
                        ])
    password = PasswordField('Password', validators=[DataRequired()])


class CreateTournament(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])

    @staticmethod
    def validate_date(field):
        if field.data < datetime.date.today():
            raise ValidationError('Date must be in the future.')
