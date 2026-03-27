import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status

from models.user import (
    RegisterRequest, SendOTPRequest, VerifyOTPRequest,
    LoginRequest, TokenResponse, UserProfileResponse, UpdateProfileRequest,
)
from db.user_repo import (
    create_user, get_user_by_email, update_user, mark_verified,
    save_otp, get_otp, delete_otp,
)
from services.auth_service import (
    hash_password, verify_password, create_token, get_current_user,
)
from services.email_service import generate_otp, send_otp_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _serialize_user(user: dict) -> UserProfileResponse:
    return UserProfileResponse(
        id=str(user["_id"]),
        username=user.get("username", ""),
        email=user.get("email", ""),
        gender=user.get("gender"),
        dob=str(user["dob"]) if user.get("dob") else None,
        profile_image=user.get("profile_image"),
        social_links=user.get("social_links"),
        is_verified=user.get("is_verified", False),
        created_at=str(user["created_at"]) if user.get("created_at") else None,
    )


# ─── POST /auth/register ──────────────────────────────────────────────────────

@router.post("/register", status_code=201)
def register(req: RegisterRequest):
    """Register a new user and send OTP to their email."""
    existing = get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user_doc = {
        "username": req.username,
        "email": req.email.lower(),
        "password": hash_password(req.password),
        "gender": req.gender,
        "dob": str(req.dob) if req.dob else None,
        "profile_image": req.profile_image,
        "social_links": req.social_links.model_dump() if req.social_links else {},
        "is_verified": False,
        "created_at": datetime.now(timezone.utc),
    }

    user_id = create_user(user_doc)

    # Send OTP
    otp = generate_otp()
    save_otp(req.email, otp)
    send_otp_email(req.email, otp)

    logger.info(f"✅ Registered user {req.email}")
    return {
        "status": "success",
        "message": "Registration successful. Check your email for the OTP.",
        "user_id": user_id,
    }


# ─── POST /auth/send-otp ──────────────────────────────────────────────────────

@router.post("/send-otp")
def send_otp(req: SendOTPRequest):
    """Resend OTP to the given email."""
    user = get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")
    if user.get("is_verified"):
        raise HTTPException(status_code=400, detail="Email already verified")

    otp = generate_otp()
    save_otp(req.email, otp)
    send_otp_email(req.email, otp)

    return {"status": "success", "message": "OTP sent to your email"}


# ─── POST /auth/verify-otp ────────────────────────────────────────────────────

@router.post("/verify-otp")
def verify_otp(req: VerifyOTPRequest):
    """Verify the OTP and mark the user's email as confirmed."""
    user = get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")
    if user.get("is_verified"):
        return {"status": "success", "message": "Email already verified"}

    stored_otp = get_otp(req.email)
    if stored_otp is None:
        raise HTTPException(status_code=400, detail="OTP expired or not found. Request a new one.")
    if stored_otp != req.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    mark_verified(req.email)
    delete_otp(req.email)

    logger.info(f"✅ Email verified: {req.email}")
    return {"status": "success", "message": "Email verified successfully"}


# ─── POST /auth/login ─────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    """Login with email + password, returns JWT access token."""
    user = get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.get("is_verified"):
        raise HTTPException(status_code=403, detail="Email not verified. Please verify your OTP first.")

    token = create_token(str(user["_id"]))
    logger.info(f"🔐 Login: {req.email}")
    return TokenResponse(access_token=token)


# ─── POST /auth/logout ────────────────────────────────────────────────────────

@router.post("/logout")
def logout():
    """
    Logout — JWT is stateless, so the client should discard the token.
    Returns a confirmation message.
    """
    return {"status": "success", "message": "Logged out successfully"}


# ─── GET /auth/me ─────────────────────────────────────────────────────────────

@router.get("/me")
def check_auth(current_user: dict = Depends(get_current_user)):
    """Validate token and return basic user info."""
    return {
        "status": "authenticated",
        "user_id": str(current_user["_id"]),
        "email": current_user.get("email"),
        "username": current_user.get("username"),
        "is_verified": current_user.get("is_verified", False),
    }


# ─── GET /auth/profile ────────────────────────────────────────────────────────

@router.get("/profile", response_model=UserProfileResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    """Return full user profile (requires valid JWT)."""
    return _serialize_user(current_user)


# ─── PATCH /auth/profile ──────────────────────────────────────────────────────

@router.patch("/profile", response_model=UserProfileResponse)
def update_profile(
    req: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update editable profile fields."""
    updates = req.model_dump(exclude_none=True)
    if "dob" in updates:
        updates["dob"] = str(updates["dob"])
    if "social_links" in updates and updates["social_links"]:
        updates["social_links"] = {
            k: v for k, v in updates["social_links"].items() if v is not None
        }

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updates["updated_at"] = datetime.now(timezone.utc)
    update_user(str(current_user["_id"]), updates)

    # Return fresh document
    from db.user_repo import get_user_by_id
    updated = get_user_by_id(str(current_user["_id"]))
    return _serialize_user(updated)
