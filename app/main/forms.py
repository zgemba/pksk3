from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField
from wtforms.validators import InputRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User
from flask_login import current_user


class EditProfileForm(Form):
    name = StringField('Ime in priimek', validators=[Length(0, 64)])
    username = StringField("Vzdevek", validators=[Length(0, 64),
                                                  Regexp('^[A-Za-zČčŠšŽž][A-Za-z0-9_.ČčŠšŽž]*$', 0,
                                                         "Vzdevek je lahko sestavljen samo samo iz črk, "
                                                         "številk, pike in podčrtaja.")])
    about_me = TextAreaField('O meni')
    submit = SubmitField('Shrani')

    def validate_username(self, field):
        old_user = User.query.filter_by(username=field.data).first()
        if old_user and old_user.id != current_user.id:
            raise ValidationError("Ta vzdevek je že zaseden")


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[InputRequired(), Length(1, 64),
                                             Email()])
    username = StringField("Vzdevek", validators=[Length(0, 64),
                                                  Regexp('^[A-Za-zČčŠšŽž][A-Za-z0-9_.ČčŠšŽž]*$', 0,
                                                         "Vzdevek je lahko sestavljen samo samo iz črk, "
                                                         "številk, pike in podčrtaja.")])
    confirmed = BooleanField('Confirmed')
    approved = BooleanField("Approved")
    role = SelectField('Role', coerce=int)
    name = StringField('Ime', validators=[Length(0, 64)])
    about_me = TextAreaField('O meni')
    submit = SubmitField('Shrani')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email je že registriran.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Uporabniško ime je zasedeno.')