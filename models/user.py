from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import date


# ─── Registration ────────────────────────────────────────────────────────────

class SocialLinks(BaseModel):
    youtube: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    dob: Optional[date] = None
    profile_image: Optional[str] = None       # URL string
    social_links: Optional[SocialLinks] = None


# ─── OTP ─────────────────────────────────────────────────────────────────────

class SendOTPRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


# ─── Login / Logout ───────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    status: str = "success"
    access_token: str
    token_type: str = "bearer"


# ─── Profile ──────────────────────────────────────────────────────────────────

class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    gender: Optional[str] = None
    dob: Optional[str] = None
    profile_image: Optional[str] = None
    social_links: Optional[Dict] = None
    is_verified: bool = False
    created_at: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    dob: Optional[date] = None
    profile_image: Optional[str] = None
    social_links: Optional[SocialLinks] = None
