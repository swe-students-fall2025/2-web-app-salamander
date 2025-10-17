from flask import request, render_template
from flask_login import login_required, current_user
from . import stats_bp
from ..db import get_db
from bson import ObjectId


@stats_bp.get("/")
@login_required
def index():
    return render_template("stats.html")
