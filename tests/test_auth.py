from app.extensions import db
from app.models import Post, StaticPage, User


def create_user(app, *, active=True, role="editor"):
    with app.app_context():
        user = User(
            email="editor@example.com",
            username="editor",
            name="Editor",
            role=role,
            active=active,
        )
        user.set_password("correct horse battery")
        db.session.add(user)
        db.session.commit()
        return user.id


def test_password_hashing(app):
    with app.app_context():
        user = User(email="a@example.com", username="a", name="A")
        user.set_password("correct horse battery")

        assert user.password_hash != "correct horse battery"
        assert user.check_password("correct horse battery")
        assert not user.check_password("wrong password")


def test_login_and_logout(client, app):
    create_user(app)

    response = client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Uspešno ste prijavljeni" in response.get_data(as_text=True)

    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert "Odjavljeni ste" in response.get_data(as_text=True)


def test_invalid_and_inactive_login_are_rejected(client, app):
    create_user(app, active=False)

    response = client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
    )
    assert response.status_code == 200
    assert "Neveljaven e-poštni naslov ali geslo" in response.get_data(as_text=True)


def test_reset_password_command(app):
    create_user(app)
    runner = app.test_cli_runner()

    result = runner.invoke(
        args=["reset-password"],
        input="editor@example.com\nnew correct password\nnew correct password\n",
    )

    assert result.exit_code == 0
    assert "Geslo za uporabnika editor je posodobljeno" in result.output
    with app.app_context():
        user = db.session.scalar(db.select(User).where(User.email == "editor@example.com"))
        assert user.check_password("new correct password")


def test_reset_password_command_rejects_short_password(app):
    runner = app.test_cli_runner()

    result = runner.invoke(args=["reset-password"], input="editor@example.com\nshort\nshort\n")

    assert result.exit_code != 0
    assert "Geslo mora imeti vsaj 8 znakov" in result.output


def test_admin_dashboard_requires_login(client):
    response = client.get("/admin/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_editor_can_open_admin_dashboard(client, app):
    create_user(app)
    client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
    )

    response = client.get("/admin/")

    assert response.status_code == 200
    assert "Upravljanje strani" in response.get_data(as_text=True)
    assert "Administracija" not in response.get_data(as_text=True)


def test_administrator_sees_management_summary(client, app):
    create_user(app, role="admin")
    client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
    )

    response = client.get("/admin/")

    assert response.status_code == 200
    assert "Administracija" in response.get_data(as_text=True)
    assert "Uporabniki: 1" in response.get_data(as_text=True)


def test_editor_can_create_publish_archive_and_delete_post(client, app):
    user_id = create_user(app)
    client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
    )

    response = client.post(
        "/admin/posts/new",
        data={"title": "Čas za Šolo", "body": "## Pozdrav\n\nTo je **vsebina**.", "publish": True},
    )
    assert response.status_code == 302

    with app.app_context():
        post = db.session.scalar(db.select(Post).where(Post.author_id == user_id))
        assert post.slug == "cas-za-solo"
        assert post.status == "published"
        assert post.published_at is not None
        assert "<h2>Pozdrav</h2>" in post.body_html
        post_id = post.id

    response = client.post(
        f"/admin/posts/{post_id}/edit",
        data={"title": "Spremenjen naslov", "body": "Arhivirana vsebina", "archive": True},
    )
    assert response.status_code == 302
    with app.app_context():
        post = db.get_or_404(Post, post_id)
        assert post.slug == "cas-za-solo"
        assert post.status == "archived"

    response = client.post(f"/admin/posts/{post_id}/delete", data={"confirm": True})
    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(Post, post_id) is None


def test_post_deletion_requires_confirmation(client, app):
    user_id = create_user(app)
    with app.app_context():
        post = Post(title="Osnutek", slug="osnutek", body="Vsebina", author_id=user_id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
    )
    response = client.post(f"/admin/posts/{post_id}/delete", data={})

    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(Post, post_id) is not None


def test_editor_can_create_publish_archive_and_delete_static_page(client, app):
    user_id = create_user(app)
    client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
    )

    response = client.post(
        "/admin/pages/new",
        data={
            "title": "O Šoli",
            "body": "## Dobrodošli\n\nPodrobnosti.",
            "show_in_nav": True,
            "nav_order": 4,
            "publish": True,
        },
    )
    assert response.status_code == 302

    with app.app_context():
        page = db.session.scalar(db.select(StaticPage).where(StaticPage.author_id == user_id))
        assert page.slug == "o-soli"
        assert page.status == "published"
        assert page.show_in_nav
        assert page.nav_order == 4
        assert "<h2>Dobrodošli</h2>" in page.body_html
        page_id = page.id

    response = client.post(
        f"/admin/pages/{page_id}/edit",
        data={"title": "Spremenjena stran", "body": "Arhivirana", "archive": True},
    )
    assert response.status_code == 302
    with app.app_context():
        page = db.session.get(StaticPage, page_id)
        assert page.slug == "o-soli"
        assert page.status == "archived"

    response = client.post(f"/admin/pages/{page_id}/delete", data={"confirm": True})
    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(StaticPage, page_id) is None
