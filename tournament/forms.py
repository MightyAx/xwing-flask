import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Regexp, ValidationError
from tournament.models_user import User


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

    def validate_date(self, field):
        if field.data < datetime.date.today():
            raise ValidationError('Date must be in the future.')


class CreatePlayer(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    faction = SelectField('Faction',
                          validators=[DataRequired()],
                          choices=[('rebel', 'Rebel Alliance'),
                                   ('empire', 'Galactic Empire'),
                                   ('scum', 'Scum & Villainy')]
                          )
    group = StringField('Group')
    submit = SubmitField('Create Player')


class AddPlayer(FlaskForm):
    player = SelectField('Player To Add', coerce=int)
    submit = SubmitField('Add Player')
