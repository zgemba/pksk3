import pytest
import shutil

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    shutil.rmtree(app.config["MEDIA_ROOT"], ignore_errors=True)


@pytest.fixture
def client(app):
    return app.test_client()
