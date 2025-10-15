from flask import render_template
from flask_login import login_required, current_user
from app.profile import bp

@bp.route("/")
# @login_required
def index():
    return render_template("profile.html")
