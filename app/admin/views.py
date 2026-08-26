from flask import render_template
from flask_login import current_user, login_required
from sqlalchemy import func

from app.admin import admin
from app.auth.decorators import editor_required
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
