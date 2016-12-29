from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from werkzeug.contrib.cache import SimpleCache

from config import config
from .filters import datetimeformat

bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
csrf = CsrfProtect()
moment = Moment()
pagedown = PageDown()
cache = SimpleCache()

login_manager = LoginManager()
login_manager.session_protection = "basic"  # zaradi flask login csrf!
login_manager.login_view = "auth.login"


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    app.add_template_filter(datetimeformat)

    return app
