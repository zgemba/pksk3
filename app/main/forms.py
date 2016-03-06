from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField, FileField
from wtforms.validators import InputRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User
from flask_login import current_user
from flask.ext.pagedown.fields import PageDownField
from ..myutils import allowed_file


class EditProfileForm(Form):
    name = StringField('Ime in priimek', validators=[Length(0, 64)])
    username = StringField("Vzdevek", validators=[Length(0, 64),
                                                  Regexp('^[A-Za-zČčŠšŽž][A-Za-z0-9_.ČčŠšŽž]*$', 0,
                                                         "Vzdevek je lahko sestavljen samo samo iz črk, "
                                                         "številk, pike in podčrtaja.")])
    about_me = TextAreaField('O meni')
    notfy_news = BooleanField('Novice')
    notfy_comments = BooleanField('Komentarji na moje prispevke')
    notfy_announcements = BooleanField('Posebna obvestila')
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
    notfy_news = BooleanField('Novice')
    notfy_comments = BooleanField('Komentarji na moje prispevke')
    notfy_announcements = BooleanField('Posebna obvestila')
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


class DodajNovicoForm(Form):
    title = StringField("Naslov", validators=[InputRequired(message="Obvezno vpiši naslov")])
    body = PageDownField("Vsebina", validators=[InputRequired(message="Obvezno vpiši vsebino")])

    # 3 potencialne slik, ni nujno, da se vse pojavijo
    img1 = FileField("Slika 1")
    img1comment = StringField("Opis")

    img2 = FileField("Slika 2")
    img2comment = StringField("Opis")

    img3 = FileField("Slika 3")
    img3comment = StringField("Opis")

    def validate_all(self, extra_validators=None):
        # tu naredi neko superduper validacijo čez prisotna polja?
        for i in range(1, 4):
            field = eval("self.img" + str(i))
            if not isinstance(field.data, str):
                    if field.data.filename != "" and not allowed_file(field.data.filename):
                        raise ValidationError("Tip datoteke ni podprt.")


class DodajKomentarForm(Form):
    body = PageDownField("Tvoj Komentar",
                         validators=[InputRequired(message="Če želiš komentirati, moraš vpisati vsebino!")])
    submit = SubmitField("Dodaj komentar")


class EditImageForm(Form):
    img = FileField("Slika")
    comment = StringField("Opis")
    delete = BooleanField("Izbriši sliko")
    headline = BooleanField("Uporabi za veliko naslovnico")
    submit = SubmitField("Shrani spremembe")

    def validate_img(self, field):
        if field.data.filename != "" and not allowed_file(field.data.filename):
            raise ValidationError("Tip datoteke ni podprt.")
