import json
import secrets

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.database import get_pool
from backend.routers.auth import get_current_user_id

router = APIRouter(prefix="/api/overlays", tags=["overlays"])


@router.get("/")
async def list_overlays(request: Request):
    """List all overlays for the current user."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    pool = await get_pool()
    if not pool:
        return JSONResponse({"overlays": []})

    rows = await pool.fetch(
        """SELECT id, name, resolution_w, resolution_h, widgets_config,
                  is_active, public_url_token, created_at, updated_at
           FROM overlays WHERE user_id = $1 ORDER BY updated_at DESC""",
        user_id,
    )
    overlays = [
        {
            "id": str(r["id"]),
            "name": r["name"],
            "resolution_w": r["resolution_w"],
            "resolution_h": r["resolution_h"],
            "widgets_config": json.loads(r["widgets_config"]) if isinstance(r["widgets_config"], str) else r["widgets_config"],
            "is_active": r["is_active"],
            "public_url_token": r["public_url_token"],
            "created_at": r["created_at"].isoformat(),
            "updated_at": r["updated_at"].isoformat(),
        }
        for r in rows
    ]
    return {"overlays": overlays}


@router.post("/")
async def create_overlay(request: Request):
    """Create a new overlay."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    name = body.get("name", "New Overlay")
    resolution_w = body.get("resolution_w", 1920)
    resolution_h = body.get("resolution_h", 1080)
    public_token = secrets.token_urlsafe(16)

    pool = await get_pool()
    if not pool:
        return JSONResponse({"error": "Database unavailable"}, status_code=503)

    row = await pool.fetchrow(
        """INSERT INTO overlays (user_id, name, resolution_w, resolution_h, public_url_token)
           VALUES ($1, $2, $3, $4, $5) RETURNING id, public_url_token""",
        user_id, name, resolution_w, resolution_h, public_token,
    )
    return {"id": str(row["id"]), "public_url_token": row["public_url_token"]}


@router.get("/{overlay_id}")
async def get_overlay(overlay_id: str, request: Request):
    """Get a specific overlay by ID."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    pool = await get_pool()
    if not pool:
        return JSONResponse({"error": "Database unavailable"}, status_code=503)

    row = await pool.fetchrow(
        """SELECT id, name, resolution_w, resolution_h, widgets_config,
                  is_active, public_url_token, created_at, updated_at
           FROM overlays WHERE id = $1 AND user_id = $2""",
        overlay_id, user_id,
    )
    if not row:
        return JSONResponse({"error": "Overlay not found"}, status_code=404)

    return {
        "id": str(row["id"]),
        "name": row["name"],
        "resolution_w": row["resolution_w"],
        "resolution_h": row["resolution_h"],
        "widgets_config": json.loads(row["widgets_config"]) if isinstance(row["widgets_config"], str) else row["widgets_config"],
        "is_active": row["is_active"],
        "public_url_token": row["public_url_token"],
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat(),
    }


@router.put("/{overlay_id}")
async def update_overlay(overlay_id: str, request: Request):
    """Update an overlay's configuration."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    pool = await get_pool()
    if not pool:
        return JSONResponse({"error": "Database unavailable"}, status_code=503)

    widgets_config = json.dumps(body.get("widgets_config", []))
    await pool.execute(
        """UPDATE overlays SET name = $3, widgets_config = $4, updated_at = NOW()
           WHERE id = $1 AND user_id = $2""",
        overlay_id, user_id, body.get("name", "Untitled"), widgets_config,
    )
    return {"status": "updated"}


@router.delete("/{overlay_id}")
async def delete_overlay(overlay_id: str, request: Request):
    """Delete an overlay."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    pool = await get_pool()
    if not pool:
        return JSONResponse({"error": "Database unavailable"}, status_code=503)

    await pool.execute(
        "DELETE FROM overlays WHERE id = $1 AND user_id = $2",
        overlay_id, user_id,
    )
    return {"status": "deleted"}


@router.get("/public/{token}")
async def get_public_overlay(token: str):
    """Get overlay data by public URL token (used by OBS Browser Source)."""
    pool = await get_pool()
    if not pool:
        return JSONResponse({"error": "Database unavailable"}, status_code=503)

    row = await pool.fetchrow(
        """SELECT id, user_id, widgets_config, resolution_w, resolution_h
           FROM overlays WHERE public_url_token = $1""",
        token,
    )
    if not row:
        return JSONResponse({"error": "Overlay not found"}, status_code=404)

    return {
        "id": str(row["id"]),
        "user_id": str(row["user_id"]),
        "widgets_config": json.loads(row["widgets_config"]) if isinstance(row["widgets_config"], str) else row["widgets_config"],
        "resolution_w": row["resolution_w"],
        "resolution_h": row["resolution_h"],
    }
