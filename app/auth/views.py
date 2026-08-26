from urllib.parse import urljoin, urlparse

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import auth
from app.auth.forms import LoginForm
from app.extensions import db
from app.models import User


def safe_next_url(target):
    if not target:
        return None
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    if redirect_url.scheme in {"http", "https"} and redirect_url.netloc == host_url.netloc:
        return redirect_url.path or "/"
    return None


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = db.session.scalar(db.select(User).where(User.email == email))
        if user is not None and user.is_active and user.check_password(form.password.data):
            login_user(user)
            flash("Uspešno ste prijavljeni.", "success")
            return redirect(safe_next_url(request.args.get("next")) or url_for("main.index"))
        flash("Neveljaven e-poštni naslov ali geslo.", "error")

    return render_template("auth/login.html", form=form)


@auth.get("/logout")
@login_required
def logout():
    logout_user()
    flash("Odjavljeni ste.", "success")
    return redirect(url_for("main.index"))
