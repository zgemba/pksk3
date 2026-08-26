from app.extensions import db
from app.models import User


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
