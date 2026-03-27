import logging
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from db.mongo import _get_db

logger = logging.getLogger(__name__)


def _users():
    db = _get_db()
    if db is None:
        raise RuntimeError("MongoDB is not connected. Set MONGO_URI.")
    return db["users"]


def _otp_store():
    db = _get_db()
    if db is None:
        raise RuntimeError("MongoDB is not connected. Set MONGO_URI.")
    return db["otp_store"]


# ─── Ensure indexes (call once at startup) ────────────────────────────────────

def ensure_indexes():
    try:
        # Unique index on email
        _users().create_index("email", unique=True)
        # TTL index on otp_store (auto-delete after 10 min)
        _otp_store().create_index(
            "created_at",
            expireAfterSeconds=600
        )
        logger.info("✅ DB indexes ensured")
    except Exception as e:
        logger.warning(f"⚠️  Could not ensure indexes: {e}")


# ─── User CRUD ────────────────────────────────────────────────────────────────

def create_user(data: dict) -> str:
    """Insert user, return inserted id string."""
    result = _users().insert_one(data)
    return str(result.inserted_id)


def get_user_by_email(email: str) -> dict | None:
    return _users().find_one({"email": email.lower()})


def get_user_by_id(user_id: str) -> dict | None:
    try:
        return _users().find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def update_user(user_id: str, fields: dict):
    _users().update_one(
        {"_id": ObjectId(user_id)},
        {"$set": fields}
    )


def mark_verified(email: str):
    _users().update_one(
        {"email": email.lower()},
        {"$set": {"is_verified": True}}
    )


# ─── OTP Helpers ─────────────────────────────────────────────────────────────

def save_otp(email: str, otp: str):
    """Upsert OTP for an email with a timestamp for TTL expiry."""
    _otp_store().update_one(
        {"email": email.lower()},
        {"$set": {"otp": otp, "created_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


def get_otp(email: str) -> str | None:
    doc = _otp_store().find_one({"email": email.lower()})
    return doc["otp"] if doc else None


def delete_otp(email: str):
    _otp_store().delete_one({"email": email.lower()})
