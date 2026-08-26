from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class PostForm(FlaskForm):
    title = StringField("Naslov", validators=[DataRequired(), Length(max=255)])
    summary = TextAreaField("Kratek povzetek", validators=[Optional(), Length(max=1000)])
    body = TextAreaField("Vsebina", validators=[DataRequired()])
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
