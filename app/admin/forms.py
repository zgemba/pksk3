from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired


class BulkEmailForm(Form):
    subject = StringField("Zadeva", validators=[InputRequired()])
    body = TextAreaField("Vsebina", validators=[InputRequired()])
    submit = SubmitField("Pošlji")
