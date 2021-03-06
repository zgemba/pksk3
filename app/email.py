from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_template_email(to, subject, template, **kwargs):
    """
    Pošlje sporočilo iz template, template polja so v kwargs.
    """
    if type(to) is not list:
        to = [to]

    app = current_app._get_current_object()
    msg = Message(app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['EMAIL_SENDER'], recipients=to)
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_message(msg):
    """
    Pošlje že narejeno sporočilo, pričakuje Message na vhodu.
    """
    app = current_app._get_current_object()
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
