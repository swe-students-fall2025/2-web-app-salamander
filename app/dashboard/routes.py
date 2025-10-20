from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from . import dashboard_bp
from ..db import get_db
from bson import ObjectId
import math, datetime as dt
import logging

logger = logging.getLogger(__name__)

PAGE_SIZE = 10

def _user_match():
    return {"$in": [ObjectId(current_user.id), current_user.id]}

@dashboard_bp.get("/")
@login_required
def index():
    db = get_db()

    # ----- filters -----
    q      = (request.args.get("q") or "").strip()
    status = (request.args.get("status") or "").strip().lower()
    sort   = (request.args.get("sort") or "deadline").lower()
    page   = max(int(request.args.get("page") or 1), 1)
    user_match = _user_match()

    logger.debug("Dashboard: user=%s page=%s q='%s' status=%s sort=%s",
                 current_user.id, page, q, status, sort)

    # ----- STATS -----
    pipeline = [
        {"$match": {"user_id": user_match}},
        {"$group": {"_id": {"$toLower": "$status"}, "count": {"$sum": 1}}},
    ]
    rows = list(db.applications.aggregate(pipeline))
    raw_counts = { (r["_id"] or "unknown"): r["count"] for r in rows }

    # bucket to keys your template uses
    stats = {
        "applied":      raw_counts.get("applied", 0),
        "interviewing": raw_counts.get("interviewing", 0)
                        + raw_counts.get("interview", 0),
        "offer":        raw_counts.get("offer", 0)
                        + raw_counts.get("offered", 0),
        "rejected":     raw_counts.get("rejected", 0),
        "accepted":     raw_counts.get("accepted", 0),
    }
    stats["total"] = sum(stats.values())

    logger.debug("Stats raw_counts=%s", raw_counts)
    logger.debug("Stats bucketed=%s (total=%s)", stats, stats["total"])

    # ----- UPCOMING  -----
    today = dt.date.today()
    soon  = today + dt.timedelta(days=14)
    upcoming = list(
        db.applications.find(
            {
                "user_id": user_match,
                "deadline": {"$gte": today.isoformat(), "$lte": soon.isoformat()},
                "status": {"$nin": ["rejected", "accepted"]},
            },
            {"company": 1, "role": 1, "deadline": 1},
        ).sort("deadline", 1).limit(5)
    )
    logger.debug("Upcoming count=%d", len(upcoming))

    # ----- MAIN LIST -----
    base = {"user_id": user_match}
    if status:
        base["status"] = status
    if q:
        base["$or"] = [
            {"company": {"$regex": q, "$options": "i"}},
            {"role":    {"$regex": q, "$options": "i"}},
        ]

    sort_key = [("deadline", 1)] if sort == "deadline" else [("updated_at", -1)]
    total = db.applications.count_documents(base)
    cursor = (db.applications.find(base)
              .sort(sort_key)
              .skip((page - 1) * PAGE_SIZE)
              .limit(PAGE_SIZE))
    applications = list(cursor)

    # stringify _id for templates (prevents ObjectId(...) rendering in URLs)
    for d in applications:
        if d.get("_id") is not None:
            d["_id"] = str(d["_id"])

    logger.debug("List total=%d page=%d/%d (query=%s)", total, page,
                 math.ceil(total / PAGE_SIZE) if total else 1, base)

    pages = math.ceil(total / PAGE_SIZE) if total else 1

    return render_template(
        "dashboard_home.html",
        applications=applications,
        stats=stats,
        upcoming=upcoming,
        filters={"q": q, "status": status, "sort": sort},
        pager={"page": page, "pages": pages, "size": PAGE_SIZE, "total": total},
    )


@dashboard_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_job():
    db = get_db()

    if request.method == "POST":
        company  = (request.form.get("company") or "").strip()
        role     = (request.form.get("role") or "").strip()
        status   = (request.form.get("status") or "applied").strip().lower()
        deadline = (request.form.get("deadline") or "").strip()

        if not company or not role:
            flash("Company and role are required.", "error")
            return render_template("dashboard/add_job.html")

        doc = {
            "user_id": ObjectId(current_user.id),
            "company": company,
            "role": role,
            "status": status,
            "deadline": deadline or None,
            "created_at": dt.datetime.utcnow().isoformat(),
            "updated_at": dt.datetime.utcnow().isoformat(),
        }
        res = db.applications.insert_one(doc)
        logger.debug("Inserted application _id=%s payload=%s", res.inserted_id, doc)

        flash("Job added successfully!", "info")
        return redirect(url_for("dashboard.index"))

    return render_template("add_job.html")

@dashboard_bp.post("/delete/<job_id>")
@login_required
def delete_job(job_id):
    """Delete a job application by its ObjectId."""
    db = get_db()
    try:
        job_oid = ObjectId(job_id)
    except Exception:
        flash("Invalid job ID.", "error")
        return redirect(url_for("dashboard.index"))

    user_match = {"$in": [ObjectId(current_user.id), current_user.id]}
    query = {
        "$and": [
            {"user_id": user_match},
            {"$or": [{"_id": job_oid}, {"_id": str(job_id)}]}
        ]
    }
    result = db.applications.delete_one(query)

    if result.deleted_count > 0:
        flash("Job deleted successfully!", "info")
    else:
        flash("Job not found or unauthorized.", "error")

    return redirect(url_for("dashboard.index"))

@dashboard_bp.route("/edit/<job_id>", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    db = get_db()
    try:
        job_oid = ObjectId(job_id)
    except Exception:
        flash("Invalid job ID.", "error")
        return redirect(url_for("dashboard.index"))

    user_match = {"$in": [ObjectId(current_user.id), current_user.id]}
    base_query = {"$and": [{"_id": job_oid}, {"user_id": user_match}]}

    job = db.applications.find_one(base_query)
    if not job:
        flash("Job not found or unauthorized.", "error")
        return redirect(url_for("dashboard.index"))

    def _norm_date(s: str):
        s = (s or "").strip()
        if not s:
            return ""
        s2 = s.replace("/", "-")
        try:
            return dt.datetime.strptime(s2, "%Y-%m-%d").date().isoformat()
        except Exception:
            return s

    if request.method == "POST":
        company_form  = (request.form.get("company") or "").strip()
        role_form     = (request.form.get("role") or "").strip()
        status_form   = (request.form.get("status") or "").strip().lower()
        applied_form  = (request.form.get("applied_date") or "").strip()
        deadline_form = (request.form.get("deadline") or "").strip()
        link_form     = (request.form.get("link") or "").strip()
        notes_form    = (request.form.get("notes") or "").strip()

        company      = company_form  or (job.get("company") or "")
        role         = role_form     or (job.get("role") or "")
        status       = status_form   or (job.get("status") or "applied")
        applied_date = _norm_date(applied_form or job.get("applied_date") or "")
        deadline     = _norm_date(deadline_form or job.get("deadline") or "")
        link         = link_form     or (job.get("link") or "")
        notes        = notes_form    or (job.get("notes") or "")

        if not company or not role:
            flash("Company and role are required.", "error")
            job.update({
                "company": company, "role": role, "status": status,
                "applied_date": applied_date or None, "deadline": deadline or None,
                "link": link, "notes": notes,
            })
            return render_template("dashboard/edit_job.html", job=job)

        update_doc = {
            "company": company,
            "role": role,
            "status": status,
            "applied_date": applied_date or None,
            "deadline": deadline or None,
            "link": link,
            "notes": notes,
            "updated_at": dt.datetime.utcnow().isoformat(),
        }

        db.applications.update_one(base_query, {"$set": update_doc})
        flash("Job updated successfully!", "info")
        return redirect(url_for("dashboard.index"))

    return render_template("edit_job.html", job=job)

@dashboard_bp.post("/status/<job_id>")
@login_required
def update_status(job_id):
    db = get_db()
    try:
        job_oid = ObjectId(job_id)
    except Exception:
        flash("Invalid job ID.", "error")
        return redirect(url_for("dashboard.index"))

    user_match = {"$in": [ObjectId(current_user.id), current_user.id]}
    base_query = {"$and": [{"_id": job_oid}, {"user_id": user_match}]}

    raw = (request.form.get("status") or "").strip().lower()
    alias = {
        "interview": "interviewing",
    }
    new_status = alias.get(raw, raw)

    allowed = {"applied", "interviewing", "offer", "rejected"}
    if new_status not in allowed:
        logger.debug("update_status: invalid status raw=%r -> mapped=%r", raw, new_status)
        flash("Invalid status.", "error")
        return redirect(url_for("dashboard.index"))

    db.applications.update_one(
        base_query,
        {"$set": {"status": new_status, "updated_at": dt.datetime.utcnow().isoformat()}}
    )
    flash("Status updated.", "info")

    return redirect(url_for(
        "dashboard.index",
        q=request.form.get("q") or "",
        status=request.form.get("current_filter_status") or "",
        sort=request.form.get("sort") or "deadline",
        page=request.form.get("page") or 1,
    ))
