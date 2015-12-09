import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "superskirvnostniključ"
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
    # FIXME
    SQLALCHEMY_DATABASE_URI = os.environ.get("PRODUCTION_DATABASE_URI") or "sqlite:///" + os.path.join(basedir, "db-devel.sqlite")
    MAIL_SERVER = "smtp.webfaction.com"
    # tu daj naknadno postgres database uri


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "sqlite": DevelopmentSqliteConfig,
    "default": DevelopmentConfig
}
