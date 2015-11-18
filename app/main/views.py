import os
import random
from datetime import datetime
from flask import render_template, redirect, url_for, abort, flash, send_from_directory, current_app, app
from flask.ext.login import login_required, current_user
from . import main
from ..models import User, Role, Post, PostImage, Comment
from ..decorators import admin_required, member_required
from .forms import EditProfileForm, EditProfileAdminForm, DodajNovicoForm, DodajKomentarForm
from app import db
from werkzeug.utils import secure_filename
from ..myutils import allowed_file, make_unique_filename


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/novice")
@main.route("/novice/<int:page>")
def novice(page=1):
    #    posts = Post.query.order_by(desc(Post.id)).paginate(page, current_app.config["ITEMS_PER_PAGE"], False)
    post = Post.query.order_by(Post.id).first()
    imgs = post.has_images
    return render_template("post.html", post=post)


@main.route("/post/<int:id>", methods=['GET', 'POST'])
def post(id):
    form = DodajKomentarForm()
    pt = Post.query.get_or_404(id)
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, author=current_user._get_current_object(), timestamp=datetime.utcnow(),
                          post=pt)
        db.session.add(comment)
        return redirect(url_for(".post", id=id))
    comments = Comment.query.all()
    return render_template("post.html", post=pt, form=form)


@main.route('/tester')
def tester():
    return render_template("tester.html")


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


@main.route("/informacije")
def informacije():
    return render_template("informacije.html")


@main.route("/urnik")
def urnik():
    return render_template("urnik.html")


#
# POST views
#
@main.route("/add_post", methods=["GET", "POST"])
@login_required
@member_required
def add_post():
    form = DodajNovicoForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        p = Post(title=title, body=body, author=current_user._get_current_object(), timestamp=datetime.utcnow())
        db.session.add(p)

        # imamo sliko?
        if form.img1.data.filename != "":
            i1_file_name = os.path.join(current_app.config["UPLOAD_SAVE_FOLDER"], secure_filename(form.img1.data.filename))
            if allowed_file(i1_file_name):
                i1_file_name = make_unique_filename(i1_file_name)
                form.img1.data.save(i1_file_name)
                image1 = PostImage(filename=i1_file_name, timestamp=datetime.utcnow(),
                                   comment=form.img1comment.data, post=p)
                db.session.add(image1)

        db.session.commit()
        return redirect(url_for(".index"))

    return render_template("add_post.html", form=form)


@login_required
@main.route('/delete_post/<int:id>', methods=["GET", "POST"])
def delete_post(id):
    pst = Post.query.get_or_404(id)
    if current_user.is_administrator() or pst.author == current_user:
        for i in PostImage.query.filter_by(post=pst):
            i.remove()
        db.session.delete(pst)
        flash("Prispevek izbrisan")
        return redirect(url_for("main.index"))
    else:
        flash("Brišete lahko samo svoje prispevke¸")


#
# COMMENT views
#
@login_required
@main.route('/delete_comment/<int:id>', methods=["GET", "POST"])
def delete_comment(id):
    cmt = Comment.query.get_or_404(id)
    if current_user.is_administrator() or cmt.author == current_user:
        db.session.delete(cmt)
        flash("Komentar izbrisan")
        return redirect(url_for("main.post", id=cmt.post.id))
    else:
        flash("Brišete lahko samo svoje komentarje")


@login_required
@admin_required
@main.route('/disable_comment/<int:id>', methods=["GET", "POST"])
def disable_comment(id):
    cmt = Comment.query.get_or_404(id)
    if current_user.is_administrator():
        cmt.disabled = True
        flash("Komentar je sktit")
        return redirect(url_for("main.post", id=cmt.post.id))
    else:
        flash("Samo za administratorje")


@login_required
@admin_required
@main.route('/enable_comment/<int:id>', methods=["GET", "POST"])
def enable_comment(id):
    cmt = Comment.query.get_or_404(id)
    if current_user.is_administrator():
        cmt.disabled = False
        flash("Komentar je spet prikazan")
        return redirect(url_for("main.post", id=cmt.post.id))
    else:
        flash("Samo za administratorje")
