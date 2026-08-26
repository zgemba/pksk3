from datetime import datetime, timezone

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.admin import admin
from app.admin.forms import ConfirmDeleteForm, PostForm, StaticPageForm
from app.auth.decorators import editor_required
from app.content import make_excerpt, render_markdown, unique_slug
from app.extensions import db
from app.models import Post, StaticPage, User


@admin.get("/")
@login_required
@editor_required
def index():
    counts = {
        "posts": db.session.scalar(db.select(func.count()).select_from(Post)) or 0,
        "published_posts": db.session.scalar(
            db.select(func.count()).select_from(Post).where(Post.status == "published")
        )
        or 0,
        "pages": db.session.scalar(db.select(func.count()).select_from(StaticPage)) or 0,
    }

    if current_user.is_admin:
        counts["users"] = db.session.scalar(db.select(func.count()).select_from(User)) or 0

    return render_template("admin/index.html", counts=counts)


def post_slug(title, post_id=None):
    def exists(candidate):
        statement = db.select(Post.id).where(Post.slug == candidate)
        if post_id is not None:
            statement = statement.where(Post.id != post_id)
        return db.session.scalar(statement) is not None

    return unique_slug(title, exists)


def page_slug(title, page_id=None):
    def exists(candidate):
        statement = db.select(StaticPage.id).where(StaticPage.slug == candidate)
        if page_id is not None:
            statement = statement.where(StaticPage.id != page_id)
        return db.session.scalar(statement) is not None

    return unique_slug(title, exists)


def update_post(post, form):
    post.title = form.title.data.strip()
    post.summary = (form.summary.data or "").strip() or make_excerpt(form.body.data)
    post.body = form.body.data
    post.body_html = render_markdown(post.body)
    if post.status == "draft":
        post.slug = post_slug(post.title, post.id)


def set_post_status(post, form):
    if form.publish.data:
        post.status = "published"
        if post.published_at is None:
            post.published_at = datetime.now(timezone.utc)
        return "Novica je objavljena."
    if form.archive.data:
        post.status = "archived"
        return "Novica je arhivirana."
    post.status = "draft"
    return "Osnutek je shranjen."


def update_page(page, form):
    page.title = form.title.data.strip()
    page.body = form.body.data
    page.body_html = render_markdown(page.body)
    page.show_in_nav = form.show_in_nav.data
    page.nav_order = form.nav_order.data or 0
    if page.status == "draft":
        page.slug = page_slug(page.title, page.id)


def set_page_status(page, form):
    if form.publish.data:
        page.status = "published"
        return "Stran je objavljena."
    if form.archive.data:
        page.status = "archived"
        return "Stran je arhivirana."
    page.status = "draft"
    return "Osnutek je shranjen."


@admin.get("/posts")
@login_required
@editor_required
def posts():
    items = db.session.scalars(db.select(Post).order_by(Post.updated_at.desc())).all()
    return render_template("admin/posts/list.html", posts=items)


@admin.route("/posts/new", methods=["GET", "POST"])
@login_required
@editor_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data.strip(),
            slug=post_slug(form.title.data),
            author=current_user,
        )
        update_post(post, form)
        message = set_post_status(post, form)
        db.session.add(post)
        db.session.commit()
        flash(message, "success")
        return redirect(url_for("admin.edit_post", post_id=post.id))

    return render_template("admin/posts/form.html", form=form, post=None)


@admin.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def edit_post(post_id):
    post = db.get_or_404(Post, post_id)
    form = PostForm(obj=post)
    delete_form = ConfirmDeleteForm()
    if form.validate_on_submit():
        update_post(post, form)
        message = set_post_status(post, form)
        db.session.commit()
        flash(message, "success")
        return redirect(url_for("admin.edit_post", post_id=post.id))

    return render_template("admin/posts/form.html", form=form, post=post, delete_form=delete_form)


@admin.post("/posts/<int:post_id>/delete")
@login_required
@editor_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    form = ConfirmDeleteForm()
    if not form.validate_on_submit():
        flash("Potrdite trajni izbris novice.", "error")
        return redirect(url_for("admin.edit_post", post_id=post.id))

    db.session.delete(post)
    db.session.commit()
    flash("Novica je trajno izbrisana.", "success")
    return redirect(url_for("admin.posts"))


@admin.get("/pages")
@login_required
@editor_required
def pages():
    items = db.session.scalars(db.select(StaticPage).order_by(StaticPage.updated_at.desc())).all()
    return render_template("admin/pages/list.html", pages=items)


@admin.route("/pages/new", methods=["GET", "POST"])
@login_required
@editor_required
def new_page():
    form = StaticPageForm()
    if form.validate_on_submit():
        page = StaticPage(
            title=form.title.data.strip(),
            slug=page_slug(form.title.data),
            author=current_user,
        )
        update_page(page, form)
        message = set_page_status(page, form)
        db.session.add(page)
        db.session.commit()
        flash(message, "success")
        return redirect(url_for("admin.edit_page", page_id=page.id))

    return render_template("admin/pages/form.html", form=form, page=None)


@admin.route("/pages/<int:page_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def edit_page(page_id):
    page = db.get_or_404(StaticPage, page_id)
    form = StaticPageForm(obj=page)
    delete_form = ConfirmDeleteForm()
    if form.validate_on_submit():
        update_page(page, form)
        message = set_page_status(page, form)
        db.session.commit()
        flash(message, "success")
        return redirect(url_for("admin.edit_page", page_id=page.id))

    return render_template("admin/pages/form.html", form=form, page=page, delete_form=delete_form)


@admin.post("/pages/<int:page_id>/delete")
@login_required
@editor_required
def delete_page(page_id):
    page = db.get_or_404(StaticPage, page_id)
    form = ConfirmDeleteForm()
    if not form.validate_on_submit():
        flash("Potrdite trajni izbris strani.", "error")
        return redirect(url_for("admin.edit_page", page_id=page.id))

    db.session.delete(page)
    db.session.commit()
    flash("Stran je trajno izbrisana.", "success")
    return redirect(url_for("admin.pages"))
