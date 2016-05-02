from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, DateTimeField
from wtforms.validators import InputRequired, Optional
from datetime import datetime
from wtforms import ValidationError
from ..models import CalendarEvent


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
    body = TextAreaField("Opis dogodka", validators=[Optional()])
    post_id = IntegerField("ID posta (če obstaja)", validators=[Optional()])
    submit = SubmitField("Shrani dogodek")

    def validate_end(form, field):
        if field.data:
            if form.start.data > form.end.data:
                raise ValidationError("Dogodek se ne more končati pred začetkom")

    def validate_post_id(form, field):
        if field.data:
            if not CalendarEvent.query.get(field.data):
                raise ValidationError("Ta post ne obstahja")