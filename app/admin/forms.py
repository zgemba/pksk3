from datetime import datetime

from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, DateTimeField, BooleanField
from wtforms import ValidationError
from wtforms.validators import InputRequired, Optional

from ..models import Post, Tag


# custom validator
def future_event(form, field):
    if field.data and (field.data < datetime.now()):
        raise ValidationError("Dogodek mora biti v prihodnosti")


class BulkEmailForm(Form):
    subject = StringField("Zadeva", validators=[InputRequired()])
    body = TextAreaField("Vsebina", validators=[InputRequired()])
    submit = SubmitField("Pošlji")


class AddEventForm(Form):
    title = StringField("Naslov", validators=[InputRequired()])
    start = DateTimeField("Začetek (d.m.l u:m)", validators=[InputRequired(), future_event], format="%d.%m.%Y %H:%M")
    end = DateTimeField("Konec (d.m.l u:m)", validators=[future_event, Optional()], format="%d.%m.%Y %H:%M")
    body = PageDownField("Opis dogodka", validators=[Optional()])
    post_id = IntegerField("ID posta (če obstaja)", validators=[Optional()])
    notify = BooleanField("Obvesti uporabnike po mailu", default=False)
    submit = SubmitField("Shrani dogodek")

    def validate_end(form, field):
        if field.data and form.start.data:
            if form.start.data > form.end.data:
                raise ValidationError("Dogodek se ne more končati pred začetkom")

    def validate_post_id(form, field):
        if field.data:
            if not Post.query.get(field.data):
                raise ValidationError("Ta post ne obstahja")


class EditEventForm(AddEventForm):
    start = DateTimeField("Začetek (d.m.l u:m)", validators=[InputRequired()], format="%d.%m.%Y %H:%M")
    end = DateTimeField("Konec (d.m.l u:m)", validators=[Optional()], format="%d.%m.%Y %H:%M")


class AddTagForm(Form):
    text = StringField("Tag", validators=[InputRequired()])
    submit = SubmitField("Shrani tag")

    def validate_text(form, field):
        if field.data:
            if field.data in Tag.all_tags():
                raise ValidationError("Ta tag že obstaja!")
