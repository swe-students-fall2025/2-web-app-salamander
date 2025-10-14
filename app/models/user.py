from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from typing import Optional, Tuple

class User(UserMixin):
    """User model wrapper for Flask-Login."""

    def __init__(self, _id, email: str, password_hash: str):
        self.id = str(_id)
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def from_mongo(doc: Optional[dict]) -> Optional["User"]:
        if not doc: return None

        id = doc.get("_id")
        if isinstance(id, ObjectId): id = str(id)

        return User(id, doc["email"], doc["password_hash"])

    @staticmethod
    def get(db, user_id: str) -> Optional["User"]:
        """
        Load by id from session. Try ObjectId first then string _id.
        """
        doc = None
        try:
            doc = db.users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            # not a valid ObjectId hex
            pass
        if doc is None:
            doc = db.users.find_one({"_id": user_id})
        return User.from_mongo(doc)

    @staticmethod
    def get_by_email(db, email: str) -> Optional["User"]:
        email = (email or "").strip().lower()
        return User.from_mongo(db.users.find_one({"email": email}))

    @staticmethod
    def create(db, email: str, password: str) -> Tuple[Optional["User"], Optional[str]]:
        email = (email or "").strip().lower()
        if not email or not password:
            return None, "Email and password are required."
        if db.users.find_one({"email": email}):
            return None, "Email already registered."
        res = db.users.insert_one({
            "email": email,
            "password_hash": generate_password_hash(password),
        })
        return User.from_mongo(db.users.find_one({"_id": res.inserted_id})), None

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
