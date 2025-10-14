
from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    from .auth import auth_bp
    from .dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    return app
