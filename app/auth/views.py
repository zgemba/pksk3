from flask import render_template, redirect, request, url_for, flash, current_app
from flask.ext.login import login_user, login_required, logout_user, current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_template_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, \
    ChangeEmailForm


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != "auth." \
                and request.endpoint != "static":
            return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("Napačno geslo")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Odjava uspela")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(email=form.email.data,
                        password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        token = new_user.generate_confirmation_token()
        send_template_email([new_user.email], "Potrdite svoj račun",
                            "auth/email/confirm", user=new_user, token=token)
        flash("Registracija je bila uspešno oddana, poslali smo vam email z navodili za potrditev.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("Potrdili ste vašo prijavo. Hvala!")
        flash("Administrator vam bo dodelil še vse ostale pravice.")
        send_template_email(current_app.config['ADMIN_EMAIL'],
                            "Zahteva za registracijo",
                            "auth/email/approve",
                            user=current_user)
    else:
        flash("Potrditvena povezava je napačna ali pa je že potekla (60 minut).")
    return redirect(url_for("main.index"))


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_template_email([current_user.email], "Potrdite svoj račun",
                        "auth/email/confirm", user=current_user, token=token)
    flash("Poslali smo vam nov potrditveni email.")
    return redirect(url_for("main.index"))


@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash("Geslo je sprememenjeno.")
            return redirect(url_for("main.index"))
        else:
            flash("Napačno geslo.")
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=["GET", "POST"])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_template_email([user.email], "Ponovno nastavite svoje geslo",
                                "auth/email/reset_password",
                                user=user, token=token,
                                next=request.args.get("next"))
        flash("Poslali smo vam email z navodili za spremembo gesla.")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash("Geslo je sprememenjeno.")
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.index"))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_template_email([new_email], "Spreemenite svoj email naslov",
                                "auth/email/change_email",
                                user=current_user, token=token)
            flash("Poslali smo vam email z navodili za spremembo vašega email naslova ")
            return redirect(url_for("main.index"))
        else:
            flash("Napačen email ali geslo.")
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash("Email naslov je bil spremenjen.")
    else:
        flash("Napačna zahteva.")
    return redirect(url_for("main.index"))
