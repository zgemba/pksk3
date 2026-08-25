import os
import unittest

from dotenv import load_dotenv
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

from app import create_app, db
from app.models import CalendarEvent, Guidebook, Permission, Post, Role, Tag, User

app = create_app(os.getenv("FLASK_CONFIG") or "default")
application = app
migrate = Migrate(app, db, directory=app.config["MIGRATIONS_FOLDER"])


@app.shell_context_processor
def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Post=Post,
        Permission=Permission,
        Role=Role,
        Guidebook=Guidebook,
        Tag=Tag,
        CalendarEvent=CalendarEvent,
    )


@app.cli.command("test")
def test_command():
    """Run the unit tests."""
    tests = unittest.TestLoader().discover("app/tests")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    raise SystemExit(0 if result.wasSuccessful() else 1)
