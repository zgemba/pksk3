# PKSK Replacement Project Handoff

Date: 2026-08-25

## Purpose

This file is a portable handoff for continuing the work in another Codex instance.

The original project was an outdated Flask application hosted on WebFaction. The modernization effort was abandoned. The agreed direction is a fresh, minimal Flask replacement targeting Opalstack.

Planning is complete. Implementation of the replacement has not started.

## Environment

- Windows 11
- Project root: `D:\Endava\EndevLocal\my-src\pksk3`
- Python 3.13 is installed and confirmed as the target runtime locally and on Opalstack.
- PyCharm is configured with the project interpreter and `.venv`.
- The replacement must run locally through PyCharm.

## Confirmed Direction

- Use Flask, not Django.
- Follow Miguel Grinberg's *Flask Web Development* application-factory and blueprint structure.
- Build a new application instead of porting old code or importing old posts.
- Keep the first release deliberately small.
- Deploy to Opalstack using a bare Git repository plus an explicit SSH deployment script triggered from PyCharm.

## Planned Structure

```text
pksk3/
  app/
    __init__.py
    models.py
    main/{__init__.py,views.py,forms.py,errors.py}
    auth/{__init__.py,views.py,forms.py}
    admin/{__init__.py,views.py,forms.py}
    templates/{base.html,main/,auth/,admin/}
    static/{css/site.css,js/,img/,vendor/bootstrap/}
  migrations/
  tests/
  config.py
  wsgi.py
  requirements.txt
  requirements-dev.txt
  .env.example
  README.md
```

The replacement should live at the repository root. Obsolete legacy modules and requirements should not remain in the production working tree.

## MVP Scope

Included:

- Public home page and news listing
- Individual news pages addressed by slugs
- Admin-editable static pages
- Site-wide editable settings
- Admin and editor accounts
- Markdown content
- One optional image per post
- Responsive Bootstrap 5 layout
- SQLite locally and PostgreSQL on Opalstack
- Light test suite
- Opalstack Git/SSH deployment workflow

Deferred:

- Old post import
- Events/calendar
- Comments
- Public registration
- Password reset email
- Google Drive integration
- Guidebooks/library
- Email notifications
- Image resizing, rotation, thumbnails, galleries, or multiple images
- Generic media model
- NavigationItem model
- Categories, tags, search, featured posts
- Revisions, approval workflow, scheduled publishing
- RSS, analytics, tracking, cookie banner, Sentry, or external monitoring

## Confirmed Models

### User

Users are content managers only. No public members.

Fields: `id`, unique indexed `email`, unique indexed `username`, `name`, `password_hash`, `role`, `active`, `created_at`, and `last_seen`.

Roles:

- `admin`: all content, settings, and user management
- `editor`: posts and static pages

Use Flask-Login. Do not create separate Role or Permission models. Create the first administrator with:

```text
flask --app wsgi create-admin
```

### Post

Fields: `id`, `title`, unique indexed `slug`, optional `summary`, Markdown `body`, rendered `body_html`, optional `image`, `image_alt`, `image_caption`, `status`, `published_at`, `created_at`, `updated_at`, and `author_id`.

Statuses: `draft`, `published`, `archived`.

URLs:

```text
GET /novice
GET /novice/<slug>
```

### StaticPage

Fields: `id`, `title`, unique indexed `slug`, Markdown `body`, rendered `body_html`, `status`, `show_in_nav`, `nav_order`, `created_at`, `updated_at`, and `author_id`.

Public URL: `GET /<slug>`.

### SiteSettings

Singleton row containing `site_name`, `site_description`, `tagline`, `contact_email`, `contact_phone`, `address`, `facebook_url`, `instagram_url`, `footer_text`, and `updated_at`.

Expose settings through a template context processor. Only administrators edit settings.

## Content Rules

- Store Markdown source and sanitized rendered HTML.
- Use a plain textarea; no rich-text JavaScript editor.
- Do not allow raw HTML or inline Markdown images.
- Allowed HTML tags: `p`, `br`, `h2`, `h3`, `h4`, `ul`, `ol`, `li`, `strong`, `em`, `blockquote`, `code`, `pre`, `a`.
- Allowed link attributes: `href`, `title`.
- Generate slugs automatically using `python-slugify`.
- Transliterate Slovenian characters such as `č`, `š`, and `ž`.
- Slugs are read-only in normal admin forms and become permanent on first publication.
- Automatically suffix collisions, for example `novica-2`.
- Handle reserved slugs automatically: `admin`, `auth`, `novice`, `static`, `login`, and `logout`.
- Generate a short plain-text excerpt when `summary` is empty.

Publishing:

- New content starts as a draft.
- Provide `Save draft` and `Publish` actions.
- Set `published_at` automatically when publishing.
- Preserve the original publication date during later edits.
- Published edits are immediately visible.
- Archiving hides content without deleting it.
- Permanent deletion requires confirmation.
- No scheduling or approval workflow.

## Images

- One optional image directly on `Post`.
- Database stores only a generated filename.
- Local media: `instance/uploads/posts/`.
- Production media: persistent directory outside deployed code.
- Accept JPEG, PNG, and WebP; maximum 5 MB.
- Validate actual image content and use random filenames.
- Require alt text if an image is uploaded.
- Do not resize or transform images.
- Serve production media through an Opalstack static application at `/media/`.
- Remove replaced or deleted files.

Configuration: `MEDIA_ROOT`, `MEDIA_URL=/media/`, and `MAX_CONTENT_LENGTH=5242880`.

## Routes

```text
GET /                         latest published posts
GET /novice                   paginated published posts
GET /novice/<slug>            published post by slug
GET /<slug>                   published static page
GET /sitemap.xml
GET /robots.txt
GET /health

GET,POST /auth/login
GET      /auth/logout

GET      /admin/
GET      /admin/posts
GET,POST /admin/posts/new
GET,POST /admin/posts/<id>/edit
POST     /admin/posts/<id>/delete
GET      /admin/pages
GET,POST /admin/pages/new
GET,POST /admin/pages/<id>/edit
POST     /admin/pages/<id>/delete
GET,POST /admin/settings
GET      /admin/users
GET,POST /admin/users/new
GET,POST /admin/users/<id>/edit
POST     /admin/users/<id>/delete
```

All state-changing actions use POST and CSRF protection.

Public listings show five newest posts on the home page and ten per page at `/novice`, newest first. Draft, archived, and future content is never public. Navigation contains Home, News, and enabled static pages ordered by `nav_order`.

## Configuration and Database

Use `Config`, `DevelopmentConfig`, `TestingConfig`, and `ProductionConfig` selected through environment variables.

- Local default: SQLite, such as `instance/dev.sqlite`.
- Tests: isolated SQLite database.
- Production: PostgreSQL on Opalstack at `localhost:5432`.
- Apply production migrations with `flask --app wsgi db upgrade`.
- Use timezone-aware UTC timestamps internally and display dates in `Europe/Ljubljana`.
- Use Slovenian for site and admin interface, with `<html lang="sl">`.

Expected `.env` keys:

```text
FLASK_CONFIG=development
SECRET_KEY=
DATABASE_URL=
MEDIA_ROOT=
MEDIA_URL=/media/
MAX_CONTENT_LENGTH=5242880
MAIL_SERVER=
MAIL_PORT=
MAIL_USE_TLS=
MAIL_USERNAME=
MAIL_PASSWORD=
```

Email keys are reserved for future use and are not MVP functionality.

## Dependencies

Runtime:

```text
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-Login
Flask-WTF
Flask-Limiter
email-validator
Markdown
bleach
Pillow
psycopg[binary]
python-dotenv
python-slugify
```

Development (`requirements-dev.txt`): `pytest`, `pytest-cov`, and `ruff`.

Use exact version pins in `requirements.txt`, selected and verified under Python 3.13. Bootstrap is a locally hosted frontend asset, not a Python dependency. Do not use Flask-Bootstrap.

## Frontend, SEO, and Security

- Use Bootstrap 5, mobile-first responsive layout, server-rendered Jinja, and one project stylesheet.
- Host Bootstrap CSS/JS locally under `app/static/vendor/bootstrap/`.
- Use semantic HTML, correct heading order, keyboard-accessible controls, and visible validation.
- No external fonts or tracking scripts.
- Add unique titles, descriptions, canonical URLs, Open Graph metadata, sitemap, and robots file.
- Use summaries or generated excerpts for descriptions.
- HTTPS only in production.
- Secure, HTTP-only, `SameSite=Lax` cookies.
- CSRF on all modifying forms.
- Generic login errors.
- Flask-Limiter login limits: 5 attempts/minute and 20/hour per IP. In-memory storage is acceptable for a low-traffic single-worker MVP; revisit if worker count increases.
- Enforce roles server-side and prevent deleting/disabling the last administrator.
- Sanitize Markdown and validate image content.
- Add security headers for content type, framing, referrers, and Content Security Policy.
- Production secrets stay only in a server-side owner-readable `.env`.
- Never enable debug mode in production or log credentials/session data.

## Testing

Keep tests deliberately light. Cover only critical behavior:

- Password handling and authorization
- Slugs
- Markdown sanitization
- Draft/published/archived visibility
- Login/logout
- One representative admin CRUD workflow
- Image validation
- Public routes and basic errors

Pre-deployment checks:

```text
ruff check
pytest
```

No local PostgreSQL environment is required unless implementation exposes a PostgreSQL-specific issue.

## Deployment

Confirmed workflow:

- Bare repository on Opalstack
- PyCharm pushes commits to the Opalstack Git remote
- Push alone does not change the running site
- PyCharm External Tool triggers an explicit SSH deployment script
- Automatic `post-receive` hooks may be considered later, but are not part of the initial workflow

Suggested server layout:

```text
/home/<user>/repos/pksk.git/
/home/<user>/apps/pksk/env/
/home/<user>/apps/pksk/project/
/home/<user>/apps/pksk/shared/.env
/home/<user>/apps/pksk/shared/media/
/home/<user>/logs/deployments/
```

The deployment script should acquire a lock, check out the exact target commit, install locked requirements, run migrations, perform an import/health check, restart uWSGI, and record the commit/result. If validation fails, it must leave the running application alone. Never put `.env`, database files, or media in Git.

Opalstack references:

- Python/uWSGI: https://docs.opalstack.com/topic-guides/python/
- Git: https://docs.opalstack.com/topic-guides/git/
- SSH/SFTP: https://docs.opalstack.com/user-guide/server-access/
- Sites: https://docs.opalstack.com/user-guide/sites/
- PostgreSQL: https://docs.opalstack.com/user-guide/postgresql-databases/

## Backups

For now, rely on Opalstack managed backups for PostgreSQL and uploaded media, and the offsite Git repository for source code.

Important limitation: Git does not protect database content or uploaded images. Independent data backups can be added later without changing the architecture.

## Repository Transition

Completed on 2026-08-25:

1. The legacy project was cleanly snapshotted at commit `acebe18`.
2. Annotated tag `legacy-snapshot-2026-08-25` was created.
3. Legacy application files were removed and committed as `e20c444` (`restart cleanup`) on `master`.
4. The cleanup commit was pushed to `origin/master`.
5. Replacement work is on branch `codex/replacement`.

The legacy snapshot remains recoverable through the tag. Do not use destructive Git commands such as `git reset --hard` or `git checkout --` without explicit approval.

Do not use destructive Git commands such as `git reset --hard` or `git checkout --` without explicit approval. Preserve current user changes in the legacy snapshot first.

The previous modernization attempt changed or added legacy files including `.gitignore`, `README.md`, `app/`, `config.py`, `drive_getter.py`, `index.py`, `manage.py`, `requirements.txt`, `.env.example`, `wsgi.py`, and this recap. Its old tests do not validate the replacement.

## Next Implementation Sequence

Completed:

1. Protected the legacy project with a snapshot tag.
2. Created `codex/replacement` and cleaned the legacy working tree.
3. Added the Flask application factory, configuration, extensions, WSGI entry point, templates, and pinned requirements.
4. Implemented the four MVP models and initial migration.
5. Added a minimal home page, `/health`, smoke tests, and Ruff configuration.
6. Configured PyCharm to use `.venv` and the `PKSK Flask` run configuration.
7. Deployed the minimal application to Opalstack and verified it through uWSGI.

Next:

1. Implement Markdown sanitization, excerpts, slug generation, and reserved-slug handling.
2. Add authentication, authorization, the `create-admin` CLI command, and login/logout.
3. Implement public news/static-page routes and admin CRUD.
4. Add uploads, Bootstrap assets, security headers, SEO metadata, sitemap, and robots file.
5. Replace production SQLite with Opalstack PostgreSQL.
6. Add the explicit SSH deployment script and deployment checks.

## Current Status

The minimal replacement is live at [www.pksk.si](https://www.pksk.si).

Local branch and commits:

```text
branch: codex/replacement
311bd23 initial Flask replacement scaffold
f16974b pin greenlet for Opalstack
```

The branch is pushed to `origin/codex/replacement`. Local Ruff and pytest checks pass (`2 passed`).

PyCharm uses `/home/blaz/PycharmProjects/pksk3/.venv/bin/python` and the `PKSK Flask` run configuration.

Opalstack deployment:

```text
SSH alias: ssh opal
server: opal6.opalstack.com
shell user: zgemba
application: /home/zgemba/apps/pksk-ng
project: /home/zgemba/apps/pksk-ng/project
shared data: /home/zgemba/apps/pksk-ng/shared
runtime: Python 3.10.21/uWSGI
deployed commit: f16974b
database: /home/zgemba/apps/pksk-ng/shared/app.sqlite
media: /home/zgemba/apps/pksk-ng/shared/media/
```

The generated uWSGI configuration loads `project/wsgi.py`, uses production settings, and the app was restarted successfully. The site currently serves the minimal page and `/health` returns `{"status":"ok"}`. The generated demo `myapp/` directory remains in the Opalstack application directory but is not used.

Important deployment follow-up: production is temporarily using SQLite. Provision PostgreSQL before adding real content, and then create a server-side owner-readable `.env` or equivalent uWSGI environment settings. A bare Git repository and explicit deployment script have not yet been implemented.
