import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "superskirvnostnikljuc"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    ADMIN_EMAIL = ["blaz.selih@gmail.com", "info@pksk.si"]
    EMAIL_SUBJECT_PREFIX = "[PKSK] "
    EMAIL_SENDER = "info@pksk.si"
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or "username"
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or "password"
    WTF_CSRF_ENABLED = True                     # a je to še potrebno?

    # Moje nastavitve za novice
    ITEMS_PER_PAGE = 10
    WORDS_PER_SHORT_ITEM = 100

    # nastavitve za upload
    BASE_FOLDER = basedir
    UPLOAD_SAVE_FOLDER = os.path.join(basedir, "app/static/img/upload")
    UPLOAD_FOLDER = "/static/img/upload"
    BANNER_FOLDER = os.path.join(basedir, "app/static/img/banner")
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_UPLOAD_DIMENSION = 1200
    THUMBNAIL_SIZE = 225

    RECAPTCHA_PARAMETERS = {"hl": "sl", "render": "explicit"}
    RECAPTCHA_DATA_ATTRS = {'theme': 'light'}
    RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY") or "recaptcha public"
    RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY") or "recaptha private"

    MIGRATIONS_FOLDER = os.path.join(basedir, "app/migrations")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI") or "postgresql://pksk:pksk@localhost:5432/test"
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MIGRATIONS_FOLDER = os.path.join(basedir, "app/post_migrations")


class DevelopmentSqliteConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI") or "sqlite:///" + os.path.join(basedir, "db-devel.sqlite")
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URI") or "sqlite:///" + os.path.join(basedir, "db-test.sqlite")


class ProductionConfig(Config):
    PRODUCTION = True
    MAIL_SERVER = "smtp.webfaction.com"
    MAIL_PORT = 25
    SQLALCHEMY_DATABASE_URI = os.environ.get("PRODUCTION_DATABASE_URI") or ""

    @classmethod
    def init_app(cls, app):
        import logging
        from logging.handlers import SMTPHandler, RotatingFileHandler

        app.logger.setLevel(logging.ERROR)

        MAIL_SERVER = "smtp.webfaction.com"
        MAIL_PORT = 25
        MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or "username"
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or "password"
        ADMIN_EMAIL = ["blaz.selih@gmail.com", "info@pksk.si"]

        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
        mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), "info@pksk.si", ADMIN_EMAIL, "PKSK failure", credentials)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        log_file = os.path.join(basedir, 'log', '') + 'pksk.log'
        file_handler = RotatingFileHandler(log_file, "a", 1*1024*1024, 10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "sqlite": DevelopmentSqliteConfig,
    "default": DevelopmentConfig
}
