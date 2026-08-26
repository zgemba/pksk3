from datetime import datetime, timezone

from flask import abort, jsonify, render_template, request

from app.extensions import db
from app.main import main
from app.models import Post, StaticPage


def published_posts():
    return (
        db.select(Post)
        .where(
            Post.status == "published",
            Post.published_at.is_not(None),
            Post.published_at <= datetime.now(timezone.utc),
        )
        .order_by(Post.published_at.desc())
    )


@main.get("/")
def index():
    posts = db.session.scalars(published_posts().limit(5)).all()
    return render_template("main/index.html", posts=posts)


@main.get("/novice")
def news():
    page_number = request.args.get("page", 1, type=int)
    page_obj = db.paginate(published_posts(), page=page_number, per_page=10, error_out=False)
    return render_template("main/news.html", page_obj=page_obj)


@main.get("/novice/<slug>")
def post(slug):
    item = db.session.scalar(published_posts().where(Post.slug == slug))
    if item is None:
        abort(404)
    return render_template("main/post.html", post=item)


@main.get("/<slug>")
def page(slug):
    item = db.session.scalar(
        db.select(StaticPage).where(StaticPage.slug == slug, StaticPage.status == "published")
    )
    if item is None:
        abort(404)
    return render_template("main/page.html", page=item)


@main.get("/health")
def health():
    return jsonify(status="ok")
