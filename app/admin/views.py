from datetime import datetime
from . import admin
from flask import render_template, redirect, url_for, flash, current_app
from flask.ext.login import login_required, current_user
from app.decorators import admin_required
from ..models import User, CalendarEvent, MailNotification, Tag
from .forms import BulkEmailForm, AddEventForm, AddTagForm
from flask.ext.mail import Message
from ..email import send_message, send_template_email
from app import db


@admin.route("/users")
@admin_required
def users():
    usrs = User.query.order_by(User.id)
    return render_template("admin/users.html", users=usrs)


@admin.route('/approve_user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def approve_user(id):
    user = User.query.get_or_404(id)
    user.approve()
    # pošlji še mail uporabniku
    send_template_email([user.email], "Prijava je potrjena!", "admin/email/approved")
    flash("Uporabnik {u} je potrjen".format(u=user.username))
    return redirect(url_for("admin.users"))


@admin.route('/delete_user/')  # za route sestavljene z js :-/
@admin.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
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
@login_required
@admin_required
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


@admin.route('/add_event', methods=['GET', 'POST'])
@login_required
@admin_required
def add_event():
    form = AddEventForm()
    if form.validate_on_submit():
        author = current_user._get_current_object()
        new_event = CalendarEvent(
            title=form.title.data, body=form.body.data, author=author, timestamp=datetime.utcnow(),
            start=form.start.data, end=form.end.data, post_id=form.post_id.data)
        db.session.add(new_event)
        db.session.commit()

        emails = User.users_to_notify(MailNotification.NEWS)
        if current_user.email in emails:  # samemu sebi ne pošiljamo mailov!
            emails.remove(current_user.email)
        for email in emails:
            send_template_email([email], "Nov dogodek v koledarju", "admin/email/new_event", event=new_event)

        return redirect(url_for("main.koledar"))

    return render_template("admin/add_event.html", form=form, title="Dodaj dogodek v koledar")


@admin.route('/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(id):
    form = AddEventForm()
    event = CalendarEvent.query.get_or_404(id)
    if form.validate_on_submit():
        event.title = form.title.data
        event.body = form.body.data
        event.start = form.start.data
        event.end = form.end.data
        event.post_id = form.post_id.data

        db.session.commit()
        return redirect(url_for("main.koledar"))

    # preload forme
    form.title.data = event.title
    form.body.data = event.body
    form.start.data = event.start
    if event.end:
        form.end.data = event.end
    if event.post_id:
        form.post_id.data = event.post_id
    return render_template("admin/add_event.html", form=form, title="Uredi dogodek v koledarju")


@admin.route('/delete_event/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_event(id):
    event = CalendarEvent.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for("main.koledar"))


@admin.route('/edit_tag/<int:id>', methods=['GET', 'POST'])
@admin.route('/edit_tag', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_tag(id=0):
    form = AddTagForm()
    all_tags = Tag.query.order_by(Tag.text)

    if form.validate_on_submit():
        if id == 0:
            newtag = Tag(text=form.text.data)
            db.session.add(newtag)
            form.text.data = ""
        else:
            tag = Tag.query.get_or_404(id)
            tag.text = form.text.data
        db.session.commit()
        return redirect(url_for("admin.edit_tag"))

    if id != 0:     # preload
        tag = Tag.query.get_or_404(id)
        form.text.data = tag.text

    return render_template("admin/edit_tag.html", form=form, tags=all_tags)


@admin.route('/delete_tag/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for("admin.edit_tag"))
