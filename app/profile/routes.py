# app/profile/routes.py

from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.profile import bp
from app.db import get_db
from datetime import datetime

from werkzeug.utils import secure_filename
from datetime import datetime
import os
import re

# ---------- helpers ----------

def _digits_only(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    plus = s.strip().startswith("+")
    digits = re.sub(r"\D", "", s)
    return ("+" + digits) if plus and digits else digits

def _uniq_list_keep_order(items, max_each=60, max_items=50):
    seen = set()
    out = []
    for it in items:
        v = (it or "").strip()
        if not v:
            continue
        key = v.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(v[:max_each])
        if len(out) >= max_items:
            break
    return out

def _to_int(val, default=None, lower=0, upper=3650):
    try:
        if val is None or val == "":
            return default
        n = int(val)
        if lower is not None:
            n = max(lower, n)
        if upper is not None:
            n = min(upper, n)
        return n
    except Exception:
        return default

# ---------- route ----------

@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    db = get_db()
    users = db.users

    user_doc = users.find_one({"email": current_user.email}) or {}

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()[:200]
        phone = _digits_only(request.form.get("phone"))
        introduction = (request.form.get("introduction") or "").strip()[:2000]

        profile_photo_path = user_doc.get("profile_photo", "")
        file = request.files.get("profile_photo")
        if file and file.filename:
            filename = secure_filename(file.filename)
            base, ext = os.path.splitext(filename)
            prefix = secure_filename((current_user.email or "user").split("@")[0]) or "user"
            safe_name = f"{prefix}{(ext or '.jpg').lower()}"
            upload_dir = os.path.join(current_app.static_folder, "uploads", "profile_photos")
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, safe_name)
            file.save(save_path)
            profile_photo_path = f"/static/uploads/profile_photos/{safe_name}"

        update_doc = {
            "name": name,
            "phone": phone,
            "introduction": introduction,
            "profile_photo": profile_photo_path,
            "updated_at": datetime.utcnow(),
        }

        users.update_one(
            {"email": current_user.email},
            {"$set": update_doc},
            upsert=True
        )

        flash("Profile updated successfully!", "info")
        return redirect(url_for("profile.index"))

    email = user_doc.get("email", current_user.email) or ""
    name = user_doc.get("name", "") or ""
    phone = user_doc.get("phone", "") or ""
    profile_photo = user_doc.get("profile_photo", "") or ""
    introduction = user_doc.get("introduction", "") or ""

    return render_template(
        "profile.html",
        email=email,
        name=name,
        phone=phone,
        profile_photo=profile_photo,
        introduction=introduction,
    )
