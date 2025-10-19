from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from . import dashboard_bp
from ..db import get_db
from bson import ObjectId
import math, datetime as dt

import logging
logger = logging.getLogger(__name__)


PAGE_SIZE = 10

@dashboard_bp.get("/")
@login_required
def index():
    db = get_db()
    user_id = ObjectId(current_user.id)

    logger.debug("USER ID %s", user_id)

    # filters
    q      = (request.args.get("q") or "").strip()
    status = (request.args.get("status") or "").strip().lower()
    sort   = request.args.get("sort") or "deadline"
    page   = max(int(request.args.get("page") or 1), 1)

    base = {"user_id": user_id}
    if status:
        base["status"] = status
    if q:
        base["$or"] = [
            {"company": {"$regex": q, "$options": "i"}},
            {"role":    {"$regex": q, "$options": "i"}},
        ]

    # stats
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    stats_raw = list(db.applications.aggregate(pipeline))
    stats = {s["_id"] or "unknown": s["count"] for s in stats_raw}
    stats["total"] = sum(stats.values())

    # upcoming deadlines
    today = dt.date.today()
    soon  = today + dt.timedelta(days=14) # upcoming defined as next 14 days
    upcoming = list(db.applications.find({
        "user_id": user_id,
        "deadline": {"$gte": today.isoformat(), "$lte": soon.isoformat()},
        "status": {"$nin": ["rejected", "accepted"]}
    }, {"company":1, "role":1, "deadline":1}).sort("deadline", 1).limit(5))

    # main list
    sort_key = [("deadline", 1)] if sort == "deadline" else [("updated_at", -1)]
    total = db.applications.count_documents(base)
    docs = (db.applications.find(base)
            .sort(sort_key)
            .skip((page-1)*PAGE_SIZE)
            .limit(PAGE_SIZE))
    
    logger.debug("FOUND %d documents", total)

    pages = math.ceil(total / PAGE_SIZE) if total else 1

    return render_template("dashboard_home.html",
                           applications=list(docs),
                           stats=stats,
                           upcoming=upcoming,
                           filters={"q": q, "status": status, "sort": sort},
                           pager={"page": page, "pages": pages, "size": PAGE_SIZE, "total": total})

@dashboard_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_job():
    db = get_db()

    if request.method == "POST":
        company = request.form.get("company")
        role = request.form.get("role")
        status = request.form.get("status")
        deadline = request.form.get("deadline")
        link = request.form.get("link")
        notes = request.form.get("notes")

        if not company or not role:
            flash("Company and role are required.", "error")
            return render_template("add_job.html")

        db.applications.insert_one({
            "user_id": ObjectId(current_user.id),
            "company": company,
            "role": role,
            "status": status or "applied",
            "deadline": deadline or None,
            "link": link or None,
            "notes": notes or None,
            "created_at": dt.datetime.utcnow().isoformat(),
            "updated_at": dt.datetime.utcnow().isoformat(),

        })
        flash("Job added successfully!", "info")
        return redirect(url_for("dashboard.index"))

    return render_template("add_job.html")

