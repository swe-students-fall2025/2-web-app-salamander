from flask import Blueprint

bp = Blueprint(
    "profile",
    __name__,
    url_prefix="/profile",
    template_folder="templates"
)

from app.profile import routes
