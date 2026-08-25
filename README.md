# PKSK

Flask application for the PKSK website.

## Local Development

Use Python 3.13. The PyCharm interpreter should point at the project virtualenv:

```powershell
D:\Endava\EndevLocal\my-src\pksk3\.venv\Scripts\python.exe
```

Install or refresh dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create a local `.env` from `.env.example` and keep it uncommitted:

```powershell
Copy-Item .env.example .env
```

For local SQLite development, keep:

```text
FLASK_CONFIG=sqlite
DEV_DATABASE_URI=sqlite:///db-devel.sqlite
```

Run tests:

```powershell
.\.venv\Scripts\python.exe -m flask --app wsgi test
```

Run the app locally:

```powershell
.\.venv\Scripts\python.exe -m flask --app wsgi run --debug
```

## Database Migrations

The Flask CLI replaces the old `Flask-Script` commands:

```powershell
.\.venv\Scripts\python.exe -m flask --app wsgi db upgrade
.\.venv\Scripts\python.exe -m flask --app wsgi db migrate -m "message"
```

## Opalstack Deployment Notes

Create a Python/uWSGI application in Opalstack, upload or clone this project into the application directory, then install dependencies into the Opalstack-provided virtualenv:

```sh
cd /home/<shell-user>/apps/<app-name>
source env/bin/activate
pip install -r pksk3/requirements.txt
```

Point `uwsgi.ini` at this app's WSGI file:

```ini
wsgi-file = /home/<shell-user>/apps/<app-name>/pksk3/wsgi.py
callable = application
touch-reload = /home/<shell-user>/apps/<app-name>/pksk3/wsgi.py
```

Set production values through a server-side `.env` file or uWSGI environment configuration:

```text
FLASK_CONFIG=production
SECRET_KEY=<strong-random-value>
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<database>
MAIL_SERVER=smtp.us.opalstack.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=<mailbox-user>
MAIL_PASSWORD=<mailbox-password>
EMAIL_SENDER=info@pksk.si
UPLOAD_SAVE_FOLDER=/home/<shell-user>/apps/<app-name>/uploads
LOG_FOLDER=/home/<shell-user>/logs/apps/<app-name>
JSON_KEY_FILE=/home/<shell-user>/apps/<app-name>/private/google-service-account.json
```

After updates:

```sh
cd /home/<shell-user>/apps/<app-name>
source env/bin/activate
pip install -r pksk3/requirements.txt
cd pksk3
flask --app wsgi db upgrade
/home/<shell-user>/apps/<app-name>/stop
/home/<shell-user>/apps/<app-name>/start
```
