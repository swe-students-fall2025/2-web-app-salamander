from flask import request, render_template
from flask_login import login_required, current_user
from . import stats_bp
from ..db import get_db
from datetime import datetime, timedelta
from collections import Counter
from bson import ObjectId 


def to_naive_datetime(dt):
    """Convert datetime to naive datetime (remove timezone info)"""
    if isinstance(dt, datetime):
        return dt.replace(tzinfo=None) if dt.tzinfo else dt
    try:
        return datetime.fromisoformat(dt).replace(tzinfo=None)
    except (ValueError, AttributeError):
        return None


@stats_bp.get("/")
@login_required
def index():
    db = get_db()
    applications = list(db.applications.find({
        "user_id": {"$in": [ObjectId(current_user.id), current_user.id]}
    }))
    total_apps = len(applications)
    now = datetime.now()

    # Last 5 applied jobs (most recent)
    recent_applications = sorted(applications, key=lambda x: to_naive_datetime(
        x.get('created_at', now)) or now, reverse=True)

    # Convert created_at to datetime objects for template
    for app in recent_applications:
        if app.get('created_at') and isinstance(app.get('created_at'), str):
            app['created_at'] = datetime.fromisoformat(
                app.get('created_at')).replace(tzinfo=None)
        elif not isinstance(app.get('created_at'), datetime):
            app['created_at'] = now

    # Top company
    companies = [app.get('company', 'Unknown') for app in applications]
    company_counts = Counter(companies)
    top_company = company_counts.most_common(
        1)[0] if company_counts else ('None', 0)

    # Total last 7 days
    seven_days_ago = now - timedelta(days=7)
    last_7_days = sum(1 for app in applications
                      if app.get('created_at') and (to_naive_datetime(app.get('created_at')) or now) >= seven_days_ago)

    # Total last 30 days
    thirty_days_ago = now - timedelta(days=30)
    last_30_days = sum(1 for app in applications
                       if app.get('created_at') and (to_naive_datetime(app.get('created_at')) or now) >= thirty_days_ago)

    # Status breakdown
    statuses = [app.get('status', 'unknown') for app in applications]
    status_counts = Counter(statuses)

    # Upcoming deadlines (next 14 days)
    upcoming_deadline = now + timedelta(days=14)
    upcoming_apps = [app for app in applications
                     if app.get('deadline') and
                     (datetime.fromisoformat(app['deadline']).replace(tzinfo=None) if isinstance(app['deadline'], str) else app['deadline']) <= upcoming_deadline and
                     (datetime.fromisoformat(app['deadline']).replace(tzinfo=None) if isinstance(app['deadline'], str) else app['deadline']) >= now]
    upcoming_apps = sorted(upcoming_apps, key=lambda x: datetime.fromisoformat(
        x['deadline']).replace(tzinfo=None) if isinstance(x['deadline'], str) else x['deadline'])[:3]

    # Convert deadline to datetime objects for template
    for app in upcoming_apps:
        if app.get('deadline') and isinstance(app.get('deadline'), str):
            app['deadline'] = datetime.fromisoformat(
                app.get('deadline')).replace(tzinfo=None)

    return render_template("stats.html",
                           total_apps=total_apps,
                           recent_applications=recent_applications,
                           top_company=top_company,
                           last_7_days=last_7_days,
                           last_30_days=last_30_days,
                           status_counts=dict(status_counts),
                           upcoming_apps=upcoming_apps)
