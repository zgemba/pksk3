from . import admin
from flask import render_template, redirect, url_for, flash, current_app
from flask.ext.login import login_required, current_user
from app.decorators import admin_required
from ..models import User
from .forms import BulkEmailForm
from flask.ext.mail import Message
from ..email import send_message


@admin.route("/users")
@admin_required
def users():
    usrs = User.query.all()
    return render_template("admin/users.html", users=usrs)


@admin.route('/approve_user/<int:id>', methods=['GET', 'POST'])
@admin_required
@login_required
def approve_user(id):
    user = User.query.get_or_404(id)
    user.approve()
    flash("Uporabnik {u} je potrjen".format(u=user.username))
    return redirect(url_for("admin.users"))


@admin.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@admin_required
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user == current_user:
        flash("Samega sebe ne smeš izbrisati!")
        return redirect(url_for("admin.users"))

    if user.posts.count() == 0 and user.comments.count() == 0:
        user.delete()
        flash("Uporabnik je bil izbrisan")
    else:
        flash("Ne morem izbrisati uporabnika, ima prispevke ali komentarje!")

    return redirect(url_for("admin.users"))


@admin.route('/bulk_email', methods=['GET', 'POST'])
@admin_required
@login_required
def bulk_email():
    form = BulkEmailForm()
    if form.validate_on_submit():
        emails = [user.email for user in User.query.all()]
        sender = current_app.config['EMAIL_SENDER']

        msg = Message(recipients=[sender], bcc=emails, subject=form.subject.data, body=form.body.data,
                      sender=sender)
        send_message(msg)
        flash("Sporočilo poslano")
        return redirect(url_for("main.index"))

    return render_template("admin/bulk_email.html", form=form)
