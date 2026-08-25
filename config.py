import os

from cachelib import SimpleCache

from app.myutils import get_from_gdrive_local  # , get_from_gdrive_remote

basedir = os.path.abspath(os.path.dirname(__file__))


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def env_list(name, default):
    value = os.environ.get(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-me"
    ADMIN_EMAIL = env_list("ADMIN_EMAIL", ["blaz.selih@gmail.com", "info@pksk.si"])
    EMAIL_SUBJECT_PREFIX = os.environ.get("EMAIL_SUBJECT_PREFIX") or "[PKSK] "
    EMAIL_SENDER = os.environ.get("EMAIL_SENDER") or "info@pksk.si"
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "localhost"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = env_bool("MAIL_USE_TLS", False)
    MAIL_USE_SSL = env_bool("MAIL_USE_SSL", False)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or None
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or None
    WTF_CSRF_ENABLED = True  # a je to še potrebno?
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Moje nastavitve za novice
    ITEMS_PER_PAGE = 10
    WORDS_PER_SHORT_ITEM = 100

    # nastavitve za upload
    BASE_FOLDER = basedir
    UPLOAD_SAVE_FOLDER = os.environ.get("UPLOAD_SAVE_FOLDER") or os.path.join(basedir, "app/static/img/upload")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or "/static/img/upload"
    BANNER_FOLDER = os.environ.get("BANNER_FOLDER") or os.path.join(basedir, "app/static/img/banner")
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_UPLOAD_DIMENSION = 800
    THUMBNAIL_SIZE = 225
    HEADLINE_SIZE = 500

    RECAPTCHA_PARAMETERS = {"hl": "sl", "render": "explicit"}
    RECAPTCHA_DATA_ATTRS = {'theme': 'light'}
    RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY") or "recaptcha public"
    RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY") or "recaptha private"

    MIGRATIONS_FOLDER = os.path.join(basedir, "app/migrations")

    # google drive api credentials
    JSON_KEY_FILE = os.environ.get("JSON_KEY_FILE") or ""

    # produkcija to overrida z memcachedd?
    CACHE = SimpleCache()
    BASEDIR = basedir

    # Username za lastnika klubskih vodničkov
    ADMIN_USERNAME = "Admin"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI") or "postgresql://pksk:pksk@localhost:5432/test"
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.googlemail.com"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = env_bool("MAIL_USE_TLS", True)
    MIGRATIONS_FOLDER = os.path.join(basedir, "app/migrations")
    GDRIVE_GETTER = get_from_gdrive_local
    BOOTSTRAP_SERVE_LOCAL = True
    ITEMS_PER_PAGE = 3  # da testiram pager
    ADMIN_USERNAME = "Blaž"


class DevelopmentSqliteConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI") or "sqlite:///" + os.path.join(basedir,
                                                                                                "db-devel.sqlite")
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.googlemail.com"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = env_bool("MAIL_USE_TLS", True)
    GDRIVE_GETTER = get_from_gdrive_local


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URI") or "sqlite:///" + os.path.join(basedir,
                                                                                                 "db-test.sqlite")
    GDRIVE_GETTER = get_from_gdrive_local


class ProductionConfig(Config):
    PRODUCTION = True
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "localhost"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = env_bool("MAIL_USE_TLS", True)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or os.environ.get("PRODUCTION_DATABASE_URI") or ""
    GDRIVE_GETTER = get_from_gdrive_local  # po updejtu oauth2client in pycripto zdaj dela okej lokalno! \o/
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME") or "https"
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)
    REMEMBER_COOKIE_SECURE = env_bool("REMEMBER_COOKIE_SECURE", True)

    @classmethod
    def init_app(cls, app):
        import logging
        from logging.handlers import SMTPHandler, RotatingFileHandler

        if app.config["SECRET_KEY"] == "dev-secret-key-change-me":
            raise RuntimeError("SECRET_KEY must be set in production")
        if not app.config["SQLALCHEMY_DATABASE_URI"]:
            raise RuntimeError("DATABASE_URL or PRODUCTION_DATABASE_URI must be set in production")

        app.logger.setLevel(logging.ERROR)

        credentials = None
        if app.config["MAIL_USERNAME"] and app.config["MAIL_PASSWORD"]:
            credentials = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])

        mail_handler = SMTPHandler(
            (app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
            app.config["EMAIL_SENDER"],
            app.config["ADMIN_EMAIL"],
            "PKSK failure",
            credentials,
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        log_folder = os.environ.get("LOG_FOLDER") or os.path.join(basedir, "log")
        os.makedirs(log_folder, exist_ok=True)
        log_file = os.path.join(log_folder, "pksk.log")
        file_handler = RotatingFileHandler(log_file, "a", 1 * 1024 * 1024, 10)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "sqlite": DevelopmentSqliteConfig,
    "default": DevelopmentConfig
}
