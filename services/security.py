import functools
import re
import secrets
import time

from flask import flash, redirect, request, session, url_for


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login to continue.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def validate_csrf(token):
    expected = session.get("_csrf_token")
    return bool(expected and token and secrets.compare_digest(expected, token))


def validate_registration(full_name, email, password, confirm_password):
    errors = []
    if len(full_name.strip()) < 2:
        errors.append("Full name must be at least 2 characters.")
    if not EMAIL_RE.match(email.strip().lower()):
        errors.append("Enter a valid email address.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    return errors


def login_rate_limited():
    now = time.time()
    attempts = [t for t in session.get("_login_attempts", []) if now - t < 900]
    session["_login_attempts"] = attempts
    return len(attempts) >= 5


def record_login_failure():
    attempts = session.get("_login_attempts", [])
    attempts.append(time.time())
    session["_login_attempts"] = attempts[-5:]


def clear_login_failures():
    session.pop("_login_attempts", None)
