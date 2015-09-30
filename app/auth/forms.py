from flask.ext.wtf import Form, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField("Email", validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField("Geslo", validators=[InputRequired()])
    remember_me = BooleanField("Ostani prijavljen")
    submit = SubmitField("Prijava")


class RegistrationForm(Form):
    email = StringField("Email", validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField("Geslo", validators=[InputRequired(),
                                                  EqualTo("password2", message="Gesli morata biti enaki")])
    password2 = PasswordField("Potrdi geslo", validators=[InputRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Zahtevaj registracijo")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Ta email je že registriran")


class ChangePasswordForm(Form):
    old_password = PasswordField('Staro geslo', validators=[InputRequired()])
    password = PasswordField('Novo geslo', validators=[
        InputRequired(), EqualTo('password2', message='Gesli morata biti enaki')])
    password2 = PasswordField('Potrdi novo geslo', validators=[InputRequired()])
    submit = SubmitField('Spremeni geslo')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[InputRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Zahtevaj novo geslo')


class PasswordResetForm(Form):
    email = StringField('Email', validators=[InputRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('Novo geslo', validators=[
        InputRequired(), EqualTo('password2', message='Gesli morata biti enaki')])
    password2 = PasswordField('Potrdi novo geslo', validators=[InputRequired()])
    submit = SubmitField('Spremeni geslo')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Neznan email naslov.')


class ChangeEmailForm(Form):
    email = StringField('Nov email', validators=[InputRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Geslo', validators=[InputRequired()])
    submit = SubmitField('Spremeni email naslov')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Ta email je že zaseden.')