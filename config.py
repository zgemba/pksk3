"""Application configuration."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'dev.sqlite'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
    MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "instance" / "uploads"))
    MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SECURITY_HEADERS_HSTS = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    MEDIA_ROOT = BASE_DIR / "instance" / "test_uploads"


class ProductionConfig(Config):
    DEBUG = False
    PREFERRED_URL_SCHEME = "https"
    SESSION_COOKIE_SECURE = True
    SECURITY_HEADERS_HSTS = True


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
