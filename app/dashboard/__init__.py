from flask import Blueprint

dashboard_bp = Blueprint(
    "dashboard",              
    __name__,
    url_prefix="/",           
    template_folder="templates",
)

from . import routes
