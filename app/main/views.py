from datetime import datetime, timezone

from flask import Response, abort, current_app, jsonify, render_template, request, send_from_directory, url_for

from app.extensions import db
from app.main import main
from app.models import Post, StaticPage
from app.timetable import TimetableUnavailable, fetch_timetable


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


@main.get("/urnik")
def timetable():
    try:
        days = fetch_timetable(
            current_app.config["TIMETABLE_API_URL"], current_app.config["TIMETABLE_API_TIMEOUT"]
        )
    except TimetableUnavailable:
        current_app.logger.warning("Timetable API is unavailable")
        return render_template("main/timetable.html", days=[], timetable_unavailable=True), 503

    return render_template("main/timetable.html", days=days, timetable_unavailable=False)


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


@main.get("/media/posts/<filename>")
def media(filename):
    return send_from_directory(current_app.config["MEDIA_ROOT"] / "posts", filename)


@main.get("/sitemap.xml")
def sitemap():
    posts = db.session.scalars(published_posts()).all()
    pages = db.session.scalars(
        db.select(StaticPage).where(StaticPage.status == "published").order_by(StaticPage.updated_at.desc())
    ).all()
    urls = [
        {"location": url_for("main.index", _external=True), "lastmod": None},
        {"location": url_for("main.news", _external=True), "lastmod": None},
        {"location": url_for("main.timetable", _external=True), "lastmod": None},
    ]
    urls.extend(
        {
            "location": url_for("main.post", slug=post.slug, _external=True),
            "lastmod": post.updated_at,
        }
        for post in posts
    )
    urls.extend(
        {
            "location": url_for("main.page", slug=page.slug, _external=True),
            "lastmod": page.updated_at,
        }
        for page in pages
    )
    return Response(render_template("main/sitemap.xml", urls=urls), mimetype="application/xml")


@main.get("/robots.txt")
def robots():
    return Response(
        render_template("main/robots.txt", sitemap_url=url_for("main.sitemap", _external=True)),
        mimetype="text/plain",
    )
