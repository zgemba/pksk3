import os
import random
from datetime import datetime
from flask import render_template, redirect, url_for, abort, flash, send_from_directory, current_app, app
from flask.ext.login import login_required, current_user
from sqlalchemy import desc
from . import main
from ..models import User, Role, Post, PostImage, Comment, Permission, MailNotification
from ..decorators import admin_required, member_required, cached
from .forms import EditProfileForm, EditProfileAdminForm, DodajNovicoForm, DodajKomentarForm, EditImageForm
from app import db
from werkzeug.utils import secure_filename
from ..myutils import allowed_file, make_unique_filename, get_from_gdrive
from ..email import send_template_email


@main.route("/")
def index():
    return redirect(url_for(".novice"))


@main.route("/novice")
@main.route("/novice/<int:page>")
def novice(page=1):
    pagination = Post.query.order_by(desc(Post.id)).paginate(page, per_page=current_app.config["ITEMS_PER_PAGE"],
                                                             error_out=False)
    posts = pagination.items
    pw = False
    if current_user.is_authenticated:
        pw = (current_user.name is None or current_user.name.strip() == "")
    return render_template("novice.html", posts=posts, pagination=pagination, profile_warn=pw)


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
        current_user.mail_notify = (int((form.notfy_announcements.data and MailNotification.ANNOUNCEMENTS)) +
                                    int((form.notfy_news.data and MailNotification.NEWS)) +
                                    int((form.notfy_comments.data and MailNotification.COMMENTS)))
        db.session.add(current_user)
        flash('Profil je bil popravljen.')
        return redirect(url_for('.user', user_id=current_user.username))

    form.name.data = current_user.name
    form.about_me.data = current_user.about_me
    form.username.data = current_user.username
    form.notfy_announcements.data = bool(current_user.mail_notify & MailNotification.ANNOUNCEMENTS)
    form.notfy_comments.data = bool(current_user.mail_notify & MailNotification.COMMENTS)
    form.notfy_news.data = bool(current_user.mail_notify & MailNotification.NEWS)

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
        user.mail_notify = (int((form.notfy_announcements.data and MailNotification.ANNOUNCEMENTS)) +
                            int((form.notfy_news.data and MailNotification.NEWS)) +
                            int((form.notfy_comments.data and MailNotification.COMMENTS)))
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
    form.notfy_announcements.data = bool(user.mail_notify & MailNotification.ANNOUNCEMENTS)
    form.notfy_comments.data = bool(user.mail_notify & MailNotification.COMMENTS)
    form.notfy_news.data = bool(user.mail_notify & MailNotification.NEWS)
    return render_template('edit_profile_admin.html', form=form, user=user)


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


@main.route("/urnik_otroci")
def urnik_otroci():
    return render_template("urnik_otroci.html")


#
# POST views
#
@main.route("/post/<int:id>", methods=['GET', 'POST'])
def post(id):
    form = DodajKomentarForm()
    pt = Post.query.get_or_404(id)
    if form.validate_on_submit():
        author = current_user._get_current_object()
        comment = Comment(body=form.body.data, author=author, timestamp=datetime.utcnow(),
                          post=pt)
        db.session.add(comment)
        # a je treba obvestiti avtorja o koemtarjih? Samega sebe ne obveščamo!
        if author != pt.author and pt.author.notify(MailNotification.COMMENTS):
            send_template_email([pt.author.email], "Nov komentar", "admin/email/new_comment", post=pt, comment=comment)

        return redirect(url_for(".post", id=id))
    return render_template("post.html", post=pt, form=form)


# refaktoriraj to v dva dela, enega za dodajanje in drugega za editiranje!
@main.route("/edit_post/<int:id>", methods=["GET", "POST"])
@login_required
@member_required
def edit_post(id):
    editing = False
    images = None
    form = DodajNovicoForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data

        if id == 0:  # dodajam nov post
            author = current_user._get_current_object()
            p = Post(title=title, body=body, author=author, timestamp=datetime.utcnow())
            db.session.add(p)

            # imamo slike?
            for i in range(1, 4):
                image_field = eval("form.img{}".format(str(i)))
                try:
                    if image_field.data.filename != "":  # imam sliko
                        comment = eval("form.img{}comment.data".format(str(i)))
                        save_image(image_field, p, comment)
                except AttributeError:  # če ni polja v formi, pol dobim AttributeError in kar ignoriram
                    pass

            # obvestim še tiste, ki so naročeni na maile o novih postih
            emails = User.users_to_notify(MailNotification.NEWS)
            if current_user.email in emails:  # samemu sebi ne pošiljamo mailov!
                emails.remove(current_user.email)
            for email in emails:
                send_template_email([email], "Nova objava", "admin/email/new_post", post=p)

        else:  # editiram obstoječega
            p = Post.query.get_or_404(id)
            p.body = body
            p.title = title
            # imamo nove slike?
            for i in range(1, 4):
                image_field = eval("form.img{}".format(str(i)))
                try:
                    if image_field.data.filename != "":  # imam sliko
                        comment = eval("form.img{}comment.data".format(str(i)))
                        save_image(image_field, p, comment)
                except AttributeError:  # če ni polja v formi, pol dobim AttributeError in kar ignoriram
                    pass

        db.session.commit()
        return redirect(url_for(".index"))

    if id != 0:  # preload forme
        editing = True
        p = Post.query.get_or_404(id)
        form.title.data = p.title
        form.body.data = p.body
        if p.has_images:
            images = p.images.all()
        else:
            images = None

    return render_template("edit_post.html", form=form, edit=editing, images=images)


def save_image(field, pst, comment):
    file_name = os.path.join(current_app.config["UPLOAD_SAVE_FOLDER"],
                             secure_filename(field.data.filename))
    if allowed_file(file_name):
        file_name = make_unique_filename(file_name)
        field.data.save(file_name)
        image = PostImage(filename=file_name, timestamp=datetime.utcnow(), comment=comment, post=pst)
        db.session.add(image)
    else:
        flash("Napačen format slike!")


@main.route('/delete_post/')  # za js route
@main.route('/delete_post/<int:id>', methods=["GET", "POST"])
@login_required
def delete_post(id):
    pst = Post.query.get_or_404(id)
    if current_user.can(Permission.ADMINISTER) or pst.author == current_user:
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
@main.route('/delete_comment/')  # za js route
@main.route('/delete_comment/<int:id>', methods=["GET", "POST"])
@login_required
def delete_comment(id):
    cmt = Comment.query.get_or_404(id)
    if current_user.can(Permission.ADMINISTER) or cmt.author == current_user:
        db.session.delete(cmt)
        flash("Komentar izbrisan")
        return redirect(url_for("main.post", id=cmt.post.id))
    else:
        flash("Brišete lahko samo svoje komentarje")


@main.route('/disable_comment/<int:id>', methods=["GET", "POST"])
@login_required
@admin_required
def disable_comment(id):
    cmt = Comment.query.get_or_404(id)
    if current_user.is_administrator():
        cmt.disabled = True
        flash("Komentar je skrit")
        return redirect(url_for("main.post", id=cmt.post.id))
    else:
        flash("Samo za administratorje")


@main.route('/enable_comment/<int:id>', methods=["GET", "POST"])
@login_required
@admin_required
def enable_comment(id):
    cmt = Comment.query.get_or_404(id)
    if current_user.is_administrator():
        cmt.disabled = False
        flash("Komentar je spet prikazan")
        return redirect(url_for("main.post", id=cmt.post.id))
    else:
        flash("Samo za administratorje")


#
# Image views
#
@main.route('/edit_image/<int:id>', methods=["GET", "POST"])
@login_required
def edit_image(id):
    image = PostImage.query.get_or_404(id)
    post = image.post
    if not(current_user.can(Permission.ADMINISTER) or post.author == current_user):
        flash("Urejate lahko samo svoje slike")
        return redirect(url_for("main.index"))

    form = EditImageForm()
    if form.validate_on_submit():
        if form.delete.data:
            image.remove()
            db.session.delete(image)
            flash("Slika izbrisana!")
            return redirect(url_for("main.edit_post", id=post.id))

        image.comment = form.comment.data
        image.is_headline = form.headline.data
        if image.is_headline:
            # zagotovi, da je to edina headline slika
            for i in post.images:
                i.is_headline = False
            image.is_headline = True

        if form.img.data.filename != "":
            image.remove()  # zbrišem staro sliko ne glede na kljukico
            db.session.delete(image)
            save_image(form.img, post, form.comment.data)
        db.session.commit()
        return redirect(url_for("main.edit_post", id=post.id))

    form.comment.data = image.comment       # preload
    form.headline.data = image.is_headline
    return render_template('edit_image.html', image=image, form=form)


#
# Ostalo
#
@main.route("/ciscenje")
@login_required
@member_required
@cached()
def razpored_ciscenja():
    sheet = get_from_gdrive("1KnfSG-v6JwLDW0vFe9E_hgDi17PfsZTPk7LuiCL9ybU")
    vals = sheet.sheet1.get_all_values()[1:]  # odstranim header row
    return render_template("razpored_ciscenja.html", members=vals)


@main.route("/bolder_3d")
def bolder_3d():
    return render_template("bolder_3d.html")


@main.route("/gradnja")
def gradnja():
    return render_template("gradnja.html")


@main.route('/test')
def test():
    return redirect(url_for(".novice"))
