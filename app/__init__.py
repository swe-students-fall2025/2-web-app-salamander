from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os

from .db import get_db
from .models.user import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"  

@login_manager.user_loader
def load_user(user_id: str):
    db = get_db()
    return User.get(db, user_id)

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SESSION_COOKIE_NAME"] = os.getenv("SESSION_COOKIE_NAME", "jobtrackr_session")

    from .auth import auth_bp
    from .dashboard import dashboard_bp
    from .profile import bp as profile_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)


    # Attach login manager to app
    login_manager.init_app(app)
    print("== URL MAP ==")
    print(app.url_map)

    return app
