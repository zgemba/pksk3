from flask import Blueprint

from app.extensions import db
from app.models import StaticPage


main = Blueprint("main", __name__)


@main.app_context_processor
def inject_navigation_pages():
    pages = db.session.scalars(
        db.select(StaticPage)
        .where(StaticPage.status == "published", StaticPage.show_in_nav.is_(True))
        .order_by(StaticPage.nav_order, StaticPage.title)
    ).all()
    return {"navigation_pages": pages}

from app.main import views  # noqa: E402,F401
