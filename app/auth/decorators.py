from functools import wraps

from flask import abort
from flask_login import current_user


def editor_required(view):
    """Allow authenticated editors and administrators."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in {"admin", "editor"}:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    """Allow administrators only."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped
