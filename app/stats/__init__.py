from flask import Blueprint

stats_bp = Blueprint(
    "stats",
    __name__,
    url_prefix="/stats",
    template_folder="templates",
)

from app.stats import routes