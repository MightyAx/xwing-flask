from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Regexp, ValidationError
from tournament.models import User


class email_exists(object):
    def __init__(self, message=None):
        if not message:
            message="Email already registered."
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
                            email_exists(message="Email already registered.")
                        ])
    name = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Register")
