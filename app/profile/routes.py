from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.profile import bp
from app.db import get_db

@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    db = get_db()
    users = db.users

    user_doc = users.find_one({"email": current_user.email}) or {}

    if request.method == "POST":
        # save updated info
        name = request.form.get("name", "").strip()
        grad_term = request.form.get("graduation_term", "").strip()

        users.update_one(
            {"email": current_user.email},
            {"$set": {"name": name, "graduation_term": grad_term}},
            upsert=True
        )

        flash("Profile updated successfully!", "info")
        return redirect(url_for("profile.index"))

    # default view profile
    name = user_doc.get("name", "")
    grad_term = user_doc.get("graduation_term", "")
    email = user_doc.get("email", current_user.email)

    return render_template("profile.html", email=email, name=name, grad_term=grad_term)
