from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models import Post, StaticPage, User


def add_author(app):
    with app.app_context():
        author = User(
            email="author@example.com",
            username="author",
            name="Author",
            password_hash="unused",
        )
        db.session.add(author)
        db.session.commit()
        return author.id


def add_post(app, author_id, *, title, slug, status="published", published_at=None):
    with app.app_context():
        post = Post(
            title=title,
            slug=slug,
            summary=f"Povzetek: {title}",
            body="Vsebina",
            body_html="<p>Vsebina</p>",
            status=status,
            published_at=published_at,
            author_id=author_id,
        )
        db.session.add(post)
        db.session.commit()
        return post.id


def test_home_and_news_only_show_current_published_posts(client, app):
    author_id = add_author(app)
    now = datetime.now(timezone.utc)
    add_post(app, author_id, title="Objavljena", slug="objavljena", published_at=now)
    add_post(app, author_id, title="Osnutek", slug="osnutek", status="draft")
    add_post(app, author_id, title="Arhiv", slug="arhiv", status="archived", published_at=now)
    add_post(app, author_id, title="Prihodnost", slug="prihodnost", published_at=now + timedelta(days=1))

    home = client.get("/")
    news = client.get("/novice")

    assert "Objavljena" in home.get_data(as_text=True)
    assert "Osnutek" not in home.get_data(as_text=True)
    assert "Arhiv" not in news.get_data(as_text=True)
    assert "Prihodnost" not in news.get_data(as_text=True)


def test_public_post_route_hides_non_public_content(client, app):
    author_id = add_author(app)
    now = datetime.now(timezone.utc)
    add_post(app, author_id, title="Javna", slug="javna", published_at=now)
    add_post(app, author_id, title="Skrita", slug="skrita", status="draft")

    assert client.get("/novice/javna").status_code == 200
    assert client.get("/novice/skrita").status_code == 404


def test_published_static_pages_render_and_fill_navigation(client, app):
    author_id = add_author(app)
    with app.app_context():
        page = StaticPage(
            title="O klubu",
            slug="o-klubu",
            body="Vsebina",
            body_html="<p>Vsebina strani</p>",
            status="published",
            show_in_nav=True,
            nav_order=2,
            author_id=author_id,
        )
        hidden = StaticPage(
            title="Osnutek strani",
            slug="osnutek-strani",
            body="Skrito",
            body_html="<p>Skrito</p>",
            status="draft",
            show_in_nav=True,
            author_id=author_id,
        )
        db.session.add_all([page, hidden])
        db.session.commit()

    home = client.get("/")
    public_page = client.get("/o-klubu")
    draft_page = client.get("/osnutek-strani")

    assert 'href="/o-klubu"' in home.get_data(as_text=True)
    assert "Osnutek strani" not in home.get_data(as_text=True)
    assert public_page.status_code == 200
    assert "Vsebina strani" in public_page.get_data(as_text=True)
    assert draft_page.status_code == 404
