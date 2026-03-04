from datetime import datetime, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from jose import jwt

from backend.config import settings
from backend.database import get_pool

router = APIRouter(prefix="/auth", tags=["auth"])

TWITCH_AUTH_URL = "https://id.twitch.tv/oauth2/authorize"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_USERS_URL = "https://api.twitch.tv/helix/users"
TWITCH_SCOPES = "user:read:email channel:read:subscriptions bits:read"

KICK_AUTH_URL = "https://id.kick.com/oauth/authorize"
KICK_TOKEN_URL = "https://id.kick.com/oauth/token"
KICK_USERS_URL = "https://api.kick.com/v1/user"
KICK_SCOPES = "user:read"


def create_jwt(user_id: str) -> str:
    """Create a JWT token for the given user ID."""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns None if invalid."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.JWTError:
        return None


async def get_current_user_id(request: Request) -> str | None:
    """Extract user_id from the session cookie."""
    token = request.cookies.get("session")
    if not token:
        return None
    payload = decode_jwt(token)
    return payload.get("user_id") if payload else None


# --- Twitch OAuth ---

@router.get("/twitch")
async def twitch_login():
    """Redirect user to Twitch OAuth authorization page."""
    params = {
        "client_id": settings.TWITCH_CLIENT_ID,
        "redirect_uri": settings.TWITCH_REDIRECT_URI,
        "response_type": "code",
        "scope": TWITCH_SCOPES,
    }
    return RedirectResponse(f"{TWITCH_AUTH_URL}?{urlencode(params)}")


@router.get("/twitch/callback")
async def twitch_callback(code: str):
    """Handle Twitch OAuth callback."""
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_res = await client.post(TWITCH_TOKEN_URL, data={
            "client_id": settings.TWITCH_CLIENT_ID,
            "client_secret": settings.TWITCH_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.TWITCH_REDIRECT_URI,
        })
        tokens = token_res.json()

        if "access_token" not in tokens:
            return RedirectResponse("/login?error=twitch_auth_failed")

        # Get Twitch user info
        user_res = await client.get(TWITCH_USERS_URL, headers={
            "Authorization": f"Bearer {tokens['access_token']}",
            "Client-Id": settings.TWITCH_CLIENT_ID,
        })
        user_data = user_res.json()

    if "data" not in user_data or not user_data["data"]:
        return RedirectResponse("/login?error=twitch_user_failed")

    twitch_user = user_data["data"][0]

    # Upsert user in database
    pool = await get_pool()
    if pool:
        row = await pool.fetchrow(
            """INSERT INTO users (twitch_id, username, display_name, avatar_url, email,
                                  twitch_access_token, twitch_refresh_token)
               VALUES ($1, $2, $3, $4, $5, $6, $7)
               ON CONFLICT (twitch_id) DO UPDATE SET
                   username = EXCLUDED.username,
                   display_name = EXCLUDED.display_name,
                   avatar_url = EXCLUDED.avatar_url,
                   email = EXCLUDED.email,
                   twitch_access_token = EXCLUDED.twitch_access_token,
                   twitch_refresh_token = EXCLUDED.twitch_refresh_token,
                   updated_at = NOW()
               RETURNING id""",
            twitch_user["id"],
            twitch_user["login"],
            twitch_user["display_name"],
            twitch_user.get("profile_image_url"),
            twitch_user.get("email"),
            tokens["access_token"],
            tokens.get("refresh_token"),
        )
        user_id = str(row["id"])
    else:
        # Development mode without database
        user_id = twitch_user["id"]

    token = create_jwt(user_id)
    response = RedirectResponse("/dashboard")
    response.set_cookie(
        "session", token, httponly=True, secure=True, samesite="lax", max_age=settings.JWT_EXPIRE_HOURS * 3600,
    )
    return response


# --- Kick OAuth ---

@router.get("/kick")
async def kick_login():
    """Redirect user to Kick OAuth authorization page."""
    params = {
        "client_id": settings.KICK_CLIENT_ID,
        "redirect_uri": settings.KICK_REDIRECT_URI,
        "response_type": "code",
        "scope": KICK_SCOPES,
    }
    return RedirectResponse(f"{KICK_AUTH_URL}?{urlencode(params)}")


@router.get("/kick/callback")
async def kick_callback(code: str):
    """Handle Kick OAuth callback."""
    async with httpx.AsyncClient() as client:
        token_res = await client.post(KICK_TOKEN_URL, data={
            "client_id": settings.KICK_CLIENT_ID,
            "client_secret": settings.KICK_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.KICK_REDIRECT_URI,
        })
        tokens = token_res.json()

        if "access_token" not in tokens:
            return RedirectResponse("/login?error=kick_auth_failed")

        user_res = await client.get(KICK_USERS_URL, headers={
            "Authorization": f"Bearer {tokens['access_token']}",
        })
        kick_user = user_res.json()

    pool = await get_pool()
    if pool:
        row = await pool.fetchrow(
            """INSERT INTO users (kick_id, username, display_name, avatar_url, email,
                                  kick_access_token, kick_refresh_token)
               VALUES ($1, $2, $3, $4, $5, $6, $7)
               ON CONFLICT (kick_id) DO UPDATE SET
                   username = EXCLUDED.username,
                   display_name = EXCLUDED.display_name,
                   avatar_url = EXCLUDED.avatar_url,
                   kick_access_token = EXCLUDED.kick_access_token,
                   kick_refresh_token = EXCLUDED.kick_refresh_token,
                   updated_at = NOW()
               RETURNING id""",
            kick_user.get("id", ""),
            kick_user.get("username", ""),
            kick_user.get("display_name", ""),
            kick_user.get("avatar_url"),
            kick_user.get("email"),
            tokens["access_token"],
            tokens.get("refresh_token"),
        )
        user_id = str(row["id"])
    else:
        user_id = str(kick_user.get("id", "dev"))

    token = create_jwt(user_id)
    response = RedirectResponse("/dashboard")
    response.set_cookie(
        "session", token, httponly=True, secure=True, samesite="lax", max_age=settings.JWT_EXPIRE_HOURS * 3600,
    )
    return response


@router.get("/logout")
async def logout():
    """Clear session cookie and redirect to landing page."""
    response = RedirectResponse("/")
    response.delete_cookie("session")
    return response


@router.get("/me")
async def get_current_user(request: Request):
    """Return current authenticated user info."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return {"authenticated": False}

    pool = await get_pool()
    if pool:
        row = await pool.fetchrow(
            "SELECT id, username, display_name, avatar_url, email, plan FROM users WHERE id = $1",
            user_id,
        )
        if row:
            return {
                "authenticated": True,
                "user": {
                    "id": str(row["id"]),
                    "username": row["username"],
                    "display_name": row["display_name"],
                    "avatar_url": row["avatar_url"],
                    "email": row["email"],
                    "plan": row["plan"],
                },
            }
    return {"authenticated": False}
