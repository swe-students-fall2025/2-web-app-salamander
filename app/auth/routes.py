from urllib.parse import urlparse, urljoin
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth_bp
from ..db import get_db
from ..models.user import User

def _is_safe_redirect(target):
    # Prevent open-redirects
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ("http", "https") and host_url.netloc == redirect_url.netloc

def _redirect_next_or(endpoint_fallback: str, **values):
    nxt = request.args.get("next") or request.form.get("next")
    if nxt and _is_safe_redirect(nxt):
        return redirect(nxt)
    return redirect(url_for(endpoint_fallback, **values))

@auth_bp.get("/login")
def login():
    return render_template("login.html", next=request.args.get("next"))

@auth_bp.post("/login")
def login_post():
    email = (request.form.get("email") or "")
    password = (request.form.get("password") or "")
    db = get_db()

    user = User.get_by_email(db, email)
    if not user or not user.check_password(password):
        flash("Invalid email or password", "error")
        return redirect(url_for("auth.login", next=request.form.get("next")))

    login_user(user, remember=True)
    return _redirect_next_or("profile.index")

@auth_bp.get("/signup")
def signup():
    return render_template("signup.html", next=request.args.get("next"))

@auth_bp.post("/signup")
def signup_post():
    email = (request.form.get("email") or "")
    password = (request.form.get("password") or "")
    if len(password) < 6:
        flash("Password must be at least 6 characters.", "error")
        return redirect(url_for("auth.signup", next=request.form.get("next")))

    db = get_db()
    user, err = User.create(db, email, password)
    if err:
        flash(err, "error")
        return redirect(url_for("auth.signup", next=request.form.get("next")))

    login_user(user, remember=True)
    return _redirect_next_or("profile.index")

@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
