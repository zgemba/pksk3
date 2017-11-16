# webfaction wsgi

import os
import site
import sys

site.addsitedir("/home/zgemba/webapps/pksk3/venv/lib/python3.5/site-packages")

sys.path.insert(0, '/home/zgemba/webapps/pksk3/venv')
sys.path.insert(0, '/home/zgemba/webapps/pksk3')

from app import create_app

application = create_app(os.getenv("FLASK_CONFIG") or "default")
