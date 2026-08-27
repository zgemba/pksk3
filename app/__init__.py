"""PKSK Flask application factory."""

import os
from logging import Formatter, StreamHandler

from flask import Flask

from config import CONFIGS
from app.extensions import csrf, db, login_manager, migrate


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_CONFIG", "development")
    config_class = CONFIGS.get(config_name, CONFIGS["development"])

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["MEDIA_ROOT"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app import models  # noqa: F401

    @app.context_processor
    def inject_site_settings():
        settings = db.session.get(models.SiteSettings, 1)
        return {"site_settings": settings or models.SiteSettings(site_name="PKSK")}

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    from app.main import main
    from app.auth import auth
    from app.admin import admin

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)

    configure_security(app)
    configure_logging(app)
    register_cli_commands(app)

    return app


def configure_security(app):
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
        )
        if app.config["SECURITY_HEADERS_HSTS"]:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response


def configure_logging(app):
    if app.debug or app.testing or app.logger.handlers:
        return
    handler = StreamHandler()
    handler.setFormatter(Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    app.logger.addHandler(handler)
    app.logger.setLevel("INFO")


def register_cli_commands(app):
    import click

    from app.models import User

    @app.cli.command("create-admin")
    def create_admin():
        """Create the first administrator account."""
        email = click.prompt("E-pošta")
        username = click.prompt("Uporabniško ime")
        name = click.prompt("Ime")
        password = click.prompt("Geslo", hide_input=True, confirmation_prompt=True)

        if len(password) < 8:
            raise click.ClickException("Geslo mora imeti vsaj 8 znakov.")

        if db.session.scalar(db.select(User).where(User.email == email.strip().lower())):
            raise click.ClickException("Uporabnik s tem e-poštnim naslovom že obstaja.")
        if db.session.scalar(db.select(User).where(User.username == username.strip())):
            raise click.ClickException("Uporabnik s tem uporabniškim imenom že obstaja.")

        user = User(
            email=email.strip().lower(),
            username=username.strip(),
            name=name.strip(),
            role="admin",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Administrator {user.username} je ustvarjen.")

    @app.cli.command("reset-password")
    def reset_password():
        """Set a new password for an existing content manager."""
        email = click.prompt("E-pošta").strip().lower()
        password = click.prompt("Novo geslo", hide_input=True, confirmation_prompt=True)

        if len(password) < 8:
            raise click.ClickException("Geslo mora imeti vsaj 8 znakov.")

        user = db.session.scalar(db.select(User).where(User.email == email))
        if user is None:
            raise click.ClickException("Uporabnik s tem e-poštnim naslovom ne obstaja.")

        user.set_password(password)
        db.session.commit()
        click.echo(f"Geslo za uporabnika {user.username} je posodobljeno.")
