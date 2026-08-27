from flask import current_app, render_template

from app.main import main


@main.app_errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html"), 403


@main.app_errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


@main.app_errorhandler(500)
def internal_error(error):
    current_app.logger.exception("Unexpected server error")
    return render_template("errors/500.html"), 500
