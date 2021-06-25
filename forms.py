from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, email


class RegisterForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired(), email()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name: ", validators=[DataRequired()])
    submit = SubmitField("Open Account!")


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired(), email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("LOG ME IN!")