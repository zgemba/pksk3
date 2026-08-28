from io import BytesIO
from pathlib import Path

from app.extensions import db
from app.models import Post, StaticPage, User
from PIL import Image


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
        data={
            "title": "Čas za Šolo",
            "body": "## Pozdrav\n\nTo je **vsebina**.",
            "show_full_on_home": True,
            "publish": True,
        },
    )
    assert response.status_code == 302

    with app.app_context():
        post = db.session.scalar(db.select(Post).where(Post.author_id == user_id))
        assert post.slug == "cas-za-solo"
        assert post.status == "published"
        assert post.published_at is not None
        assert "<h2>Pozdrav</h2>" in post.body_html
        assert post.show_full_on_home
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
        assert not post.show_full_on_home

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


def test_settings_and_user_management_are_admin_only(client, app):
    create_user(app)
    client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
    )

    assert client.get("/admin/settings").status_code == 403
    assert client.get("/admin/users").status_code == 403


def test_administrator_can_save_settings_and_manage_users(client, app):
    admin_id = create_user(app, role="admin")
    client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
    )

    response = client.post(
        "/admin/settings",
        data={
            "site_name": "PKSK test",
            "site_description": "Opis",
            "contact_email": "info@example.com",
            "footer_text": "Noga strani",
        },
    )
    assert response.status_code == 302
    assert "Noga strani" in client.get("/").get_data(as_text=True)

    response = client.post(
        "/admin/users/new",
        data={
            "email": "new@example.com",
            "username": "new-editor",
            "name": "New Editor",
            "role": "editor",
            "active": True,
            "password": "a safe password",
        },
    )
    assert response.status_code == 302
    with app.app_context():
        editor = db.session.scalar(db.select(User).where(User.email == "new@example.com"))
        assert editor is not None
        assert editor.check_password("a safe password")
        editor_id = editor.id

    response = client.post(f"/admin/users/{editor_id}/delete", data={"confirm": True})
    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(User, editor_id) is None
        assert db.session.get(User, admin_id) is not None


def test_last_administrator_cannot_be_disabled_or_deleted(client, app):
    admin_id = create_user(app, role="admin")
    client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
    )

    response = client.post(
        f"/admin/users/{admin_id}/edit",
        data={
            "email": "editor@example.com",
            "username": "editor",
            "name": "Editor",
            "role": "admin",
        },
    )
    assert response.status_code == 200
    assert "Zadnjega aktivnega administratorja" in response.get_data(as_text=True)

    response = client.post(f"/admin/users/{admin_id}/delete", data={"confirm": True})
    assert response.status_code == 302
    with app.app_context():
        admin = db.session.get(User, admin_id)
        assert admin is not None
        assert admin.active
        assert admin.role == "admin"


def test_post_image_upload_replace_and_deletion(client, app):
    create_user(app)
    client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
    )
    image_bytes = BytesIO()
    Image.new("RGB", (1, 1), color="white").save(image_bytes, format="PNG")

    response = client.post(
        "/admin/posts/new",
        data={
            "title": "Novica s sliko",
            "body": "Vsebina",
            "image": (BytesIO(image_bytes.getvalue()), "image.jpg"),
            "image_alt": "Opis slike",
            "image_caption": "Napis",
            "save_draft": True,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 302
    with app.app_context():
        post = db.session.scalar(db.select(Post).where(Post.slug == "novica-s-sliko"))
        assert post.image is not None
        assert post.image.endswith(".png")
        first_image = post.image
        assert (Path(app.config["MEDIA_ROOT"]) / "posts" / first_image).is_file()
        post_id = post.id

    assert client.get(f"/media/posts/{first_image}").status_code == 200

    response = client.post(
        f"/admin/posts/{post_id}/edit",
        data={
            "title": "Novica s sliko",
            "body": "Vsebina",
            "image": (BytesIO(image_bytes.getvalue()), "replacement.png"),
            "image_alt": "Nov opis",
            "save_draft": True,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 302
    with app.app_context():
        post = db.session.get(Post, post_id)
        assert post.image != first_image
        assert not (Path(app.config["MEDIA_ROOT"]) / "posts" / first_image).exists()
        second_image = post.image

    response = client.post(
        f"/admin/posts/{post_id}/edit",
        data={"title": "Novica s sliko", "body": "Vsebina", "publish": True},
    )
    assert response.status_code == 302
    with app.app_context():
        post = db.session.get(Post, post_id)
        assert post.status == "published"
        assert post.image == second_image

    client.post(f"/admin/posts/{post_id}/delete", data={"confirm": True})
    assert not (Path(app.config["MEDIA_ROOT"]) / "posts" / second_image).exists()


def test_post_image_requires_alt_text_and_rejects_invalid_content(client, app):
    create_user(app)
    client.post(
        "/auth/login",
        data={"email": "editor@example.com", "password": "correct horse battery"},
    )

    response = client.post(
        "/admin/posts/new",
        data={
            "title": "Manjka opis",
            "body": "Vsebina",
            "image": (BytesIO(b"not an image"), "image.png"),
            "save_draft": True,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert "Opis slike je obvezen" in response.get_data(as_text=True)
    with app.app_context():
        assert db.session.scalar(db.select(Post).where(Post.slug == "manjka-opis")) is None

    response = client.post(
        "/admin/posts/new",
        data={
            "title": "Napačna slika",
            "body": "Vsebina",
            "image": (BytesIO(b"not an image"), "image.png"),
            "image_alt": "Opis",
            "save_draft": True,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert "Datoteka ni veljavna slika" in response.get_data(as_text=True)
