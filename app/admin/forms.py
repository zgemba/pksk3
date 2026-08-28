from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import BooleanField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, URL


class PostForm(FlaskForm):
    title = StringField("Naslov", validators=[DataRequired(), Length(max=255)])
    summary = TextAreaField("Kratek povzetek", validators=[Optional(), Length(max=1000)])
    body = TextAreaField("Vsebina", validators=[DataRequired()])
    show_full_on_home = BooleanField("Objavi vso vsebino na prvi strani")
    image = FileField("Slika")
    image_alt = StringField("Opis slike", validators=[Optional(), Length(max=255)])
    image_caption = StringField("Napis ob sliki", validators=[Optional(), Length(max=255)])
    remove_image = BooleanField("Odstrani trenutno sliko")
    save_draft = SubmitField("Shrani osnutek")
    publish = SubmitField("Objavi")
    archive = SubmitField("Arhiviraj")


class ConfirmDeleteForm(FlaskForm):
    confirm = BooleanField("Razumem, da bo vsebina trajno izbrisana.", validators=[DataRequired()])
    submit = SubmitField("Trajno izbriši")


class StaticPageForm(FlaskForm):
    title = StringField("Naslov", validators=[DataRequired(), Length(max=255)])
    body = TextAreaField("Vsebina", validators=[DataRequired()])
    show_in_nav = BooleanField("Prikaži v navigaciji")
    nav_order = IntegerField("Vrstni red v navigaciji", validators=[Optional(), NumberRange(min=0)])
    save_draft = SubmitField("Shrani osnutek")
    publish = SubmitField("Objavi")
    archive = SubmitField("Arhiviraj")


class SiteSettingsForm(FlaskForm):
    site_name = StringField("Ime strani", validators=[DataRequired(), Length(max=255)])
    site_description = TextAreaField("Opis strani", validators=[Optional()])
    tagline = StringField("Slogan", validators=[Optional(), Length(max=255)])
    contact_email = StringField("Kontaktni e-poštni naslov", validators=[Optional(), Email(), Length(max=255)])
    contact_phone = StringField("Kontaktni telefon", validators=[Optional(), Length(max=80)])
    address = TextAreaField("Naslov", validators=[Optional()])
    facebook_url = StringField("Facebook", validators=[Optional(), URL(), Length(max=500)])
    instagram_url = StringField("Instagram", validators=[Optional(), URL(), Length(max=500)])
    footer_text = TextAreaField("Besedilo noge", validators=[Optional()])
    submit = SubmitField("Shrani nastavitve")


class UserCreateForm(FlaskForm):
    email = StringField("E-pošta", validators=[DataRequired(), Email(), Length(max=255)])
    username = StringField("Uporabniško ime", validators=[DataRequired(), Length(max=80)])
    name = StringField("Ime", validators=[DataRequired(), Length(max=120)])
    role = SelectField("Vloga", choices=[("editor", "Urednik"), ("admin", "Administrator")])
    active = BooleanField("Aktiven", default=True)
    password = PasswordField("Začasno geslo", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Ustvari uporabnika")


class UserEditForm(FlaskForm):
    email = StringField("E-pošta", validators=[DataRequired(), Email(), Length(max=255)])
    username = StringField("Uporabniško ime", validators=[DataRequired(), Length(max=80)])
    name = StringField("Ime", validators=[DataRequired(), Length(max=120)])
    role = SelectField("Vloga", choices=[("editor", "Urednik"), ("admin", "Administrator")])
    active = BooleanField("Aktiven")
    password = PasswordField("Novo geslo", validators=[Optional(), Length(min=8)])
    submit = SubmitField("Shrani uporabnika")


class ConfirmUserDeleteForm(FlaskForm):
    confirm = BooleanField("Razumem, da bo uporabnik trajno izbrisan.", validators=[DataRequired()])
    submit = SubmitField("Trajno izbriši uporabnika")
