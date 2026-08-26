from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField("E-pošta", validators=[DataRequired(), Email()])
    password = PasswordField("Geslo", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Prijava")
