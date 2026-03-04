import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.database import get_pool
from backend.routers.auth import get_current_user_id

router = APIRouter(prefix="/api/widgets", tags=["widgets"])


@router.get("/{overlay_id}")
async def list_widgets(overlay_id: str, request: Request):
    """List all widgets for a given overlay."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    pool = await get_pool()
    if not pool:
        return JSONResponse({"widgets": []})

    rows = await pool.fetch(
        """SELECT id, widget_type, name, config, position_x, position_y,
                  width, height, z_index, is_visible
           FROM user_widgets WHERE overlay_id = $1 AND user_id = $2
           ORDER BY z_index ASC""",
        overlay_id, user_id,
    )
    widgets = [
        {
            "id": str(r["id"]),
            "widget_type": r["widget_type"],
            "name": r["name"],
            "config": json.loads(r["config"]) if isinstance(r["config"], str) else r["config"],
            "position_x": r["position_x"],
            "position_y": r["position_y"],
            "width": r["width"],
            "height": r["height"],
            "z_index": r["z_index"],
            "is_visible": r["is_visible"],
        }
        for r in rows
    ]
    return {"widgets": widgets}


@router.post("/{overlay_id}")
async def add_widget(overlay_id: str, request: Request):
    """Add a widget to an overlay."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    pool = await get_pool()
    if not pool:
        return JSONResponse({"error": "Database unavailable"}, status_code=503)

    row = await pool.fetchrow(
        """INSERT INTO user_widgets (user_id, overlay_id, widget_type, name, config,
                                     position_x, position_y, width, height, z_index)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING id""",
        user_id,
        overlay_id,
        body.get("widget_type", "alert-box"),
        body.get("name", "New Widget"),
        json.dumps(body.get("config", {})),
        body.get("position_x", 0),
        body.get("position_y", 0),
        body.get("width", 300),
        body.get("height", 200),
        body.get("z_index", 1),
    )
    return {"id": str(row["id"])}


@router.put("/{widget_id}")
async def update_widget(widget_id: str, request: Request):
    """Update a widget's properties."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    pool = await get_pool()
    if not pool:
        return JSONResponse({"error": "Database unavailable"}, status_code=503)

    await pool.execute(
        """UPDATE user_widgets SET
               config = $3, position_x = $4, position_y = $5,
               width = $6, height = $7, z_index = $8, is_visible = $9
           WHERE id = $1 AND user_id = $2""",
        widget_id,
        user_id,
        json.dumps(body.get("config", {})),
        body.get("position_x", 0),
        body.get("position_y", 0),
        body.get("width", 300),
        body.get("height", 200),
        body.get("z_index", 1),
        body.get("is_visible", True),
    )
    return {"status": "updated"}


@router.delete("/{widget_id}")
async def delete_widget(widget_id: str, request: Request):
    """Delete a widget."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    pool = await get_pool()
    if not pool:
        return JSONResponse({"error": "Database unavailable"}, status_code=503)

    await pool.execute(
        "DELETE FROM user_widgets WHERE id = $1 AND user_id = $2",
        widget_id, user_id,
    )
    return {"status": "deleted"}
