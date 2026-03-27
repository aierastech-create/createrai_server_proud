import os
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# MongoDB client (lazy init)
_db = None


def _get_db():
    """Get MongoDB database, returns None if unavailable."""
    global _db
    if _db is not None:
        return _db

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        logger.info("ℹ️  MONGO_URI not set — history saving disabled")
        return None

    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
        # Test connection
        client.admin.command("ping")
        _db = client["createrai"]
        logger.info("✅ Connected to MongoDB")
        return _db
    except Exception as e:
        logger.warning(f"⚠️  MongoDB unavailable: {e} — history saving disabled")
        return None


def save_history(user_id: str, feature: str, input_text: str, output: str):
    """Save generation history to MongoDB. Silently skips if DB unavailable."""
    db = _get_db()
    if db is None:
        return

    try:
        db.history.insert_one({
            "user_id": user_id,
            "feature": feature,
            "input": input_text,
            "output": output,
            "created_at": datetime.now(timezone.utc),
        })
    except Exception as e:
        logger.warning(f"⚠️  Failed to save history: {e}")
