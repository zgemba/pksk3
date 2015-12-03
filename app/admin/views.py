from . import admin
from .. import db
from flask import render_template, redirect, request, url_for, flash, current_app
from flask.ext.login import login_required
from app.decorators import admin_required
from ..models import User
from ..email import send_email


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
    flash("Uporabnik je potrjen")
    return redirect(url_for("admin.users"))
