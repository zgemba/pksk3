from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from wtforms.validators import InputRequired, Email, Length, EqualTo

from ..models import User


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField("Geslo", validators=[InputRequired()])
    remember_me = BooleanField("Ostani prijavljen")
    submit = SubmitField("Prijava")


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField("Geslo", validators=[InputRequired(),
                                                  EqualTo("password2", message="Gesli morata biti enaki")])
    password2 = PasswordField("Potrdi geslo", validators=[InputRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Zahtevaj registracijo")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Ta email je že registriran")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Staro geslo', validators=[InputRequired()])
    password = PasswordField('Novo geslo', validators=[
        InputRequired(), EqualTo('password2', message='Gesli morata biti enaki')])
    password2 = PasswordField('Potrdi novo geslo', validators=[InputRequired()])
    submit = SubmitField('Spremeni geslo')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Zahtevaj novo geslo')


class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('Novo geslo', validators=[
        InputRequired(), EqualTo('password2', message='Gesli morata biti enaki')])
    password2 = PasswordField('Potrdi novo geslo', validators=[InputRequired()])
    submit = SubmitField('Spremeni geslo')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Neznan email naslov.')


class ChangeEmailForm(FlaskForm):
    email = StringField('Nov email', validators=[InputRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Geslo', validators=[InputRequired()])
    submit = SubmitField('Spremeni email naslov')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Ta email je že zaseden.')