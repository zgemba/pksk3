import os
import random

from flask import render_template, redirect, url_for, abort, flash, send_from_directory, current_app, app
from flask.ext.login import login_required, current_user

from . import main
from ..models import Permission, User, Role
from ..decorators import admin_required
from .forms import EditProfileForm, EditProfileAdminForm
from app import db


@main.route("/")
def index():
    return render_template("index.html")


@main.route('/user/<user_id>')
def user(user_id):
    try:
        id = int(user_id)
        user = User.query.filter_by(id=id).first()
    except:
        user = User.query.filter_by(username=user_id).first()

    if user is None:
        flash("Uporabnik ne obstaja")
        abort(404)
    return render_template("user.html", user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        current_user.username = form.username.data
        db.session.add(current_user)
        flash('Profil je bil popravljen.')
        return redirect(url_for('.user', user_id=current_user.username))
    form.name.data = current_user.name
    form.about_me.data = current_user.about_me
    form.username.data = current_user.username
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.approved = form.approved.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('Profil je bil popravljen.')
        return redirect(url_for('.user', user_id=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.approved.data = user.approved
    form.role.data = user.role_id
    form.name.data = user.name
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route("/random_banner")
def random_banner():
    banners = [f for f in os.listdir(current_app.config["BANNER_FOLDER"]) if f.endswith(".jpg")]
    banner = random.choice(banners)
    return send_from_directory(current_app.config['BANNER_FOLDER'],
                               banner)
