"""PKSK Flask application factory."""

import os

from flask import Flask

from config import CONFIGS
from app.extensions import db, login_manager, migrate


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

    from app import models  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    from app.main import main

    app.register_blueprint(main)

    return app
