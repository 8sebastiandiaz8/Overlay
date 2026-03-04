import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.database import get_pool
from backend.routers.auth import get_current_user_id

router = APIRouter(prefix="/store", tags=["store"])


@router.get("/api/products")
async def list_products(
    product_type: str | None = None,
    tag: str | None = None,
):
    """List published products, optionally filtered by type or tag."""
    pool = await get_pool()
    if not pool:
        return {"products": []}

    query = "SELECT * FROM products WHERE is_published = true"
    params: list = []
    idx = 1

    if product_type:
        query += f" AND product_type = ${idx}"
        params.append(product_type)
        idx += 1

    if tag:
        query += f" AND ${ idx } = ANY(tags)"
        params.append(tag)
        idx += 1

    query += " ORDER BY created_at DESC"
    rows = await pool.fetch(query, *params)
    products = [
        {
            "id": str(r["id"]),
            "name": r["name"],
            "description": r["description"],
            "price": float(r["price"]),
            "currency": r["currency"],
            "product_type": r["product_type"],
            "preview_url": r["preview_url"],
            "tags": r["tags"],
            "downloads_count": r["downloads_count"],
        }
        for r in rows
    ]
    return {"products": products}


@router.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get a specific product by ID."""
    pool = await get_pool()
    if not pool:
        return JSONResponse({"error": "Database unavailable"}, status_code=503)

    row = await pool.fetchrow("SELECT * FROM products WHERE id = $1", product_id)
    if not row:
        return JSONResponse({"error": "Product not found"}, status_code=404)

    return {
        "id": str(row["id"]),
        "name": row["name"],
        "description": row["description"],
        "price": float(row["price"]),
        "currency": row["currency"],
        "product_type": row["product_type"],
        "preview_url": row["preview_url"],
        "download_files": json.loads(row["download_files"]) if isinstance(row["download_files"], str) else row["download_files"],
        "tags": row["tags"],
        "downloads_count": row["downloads_count"],
    }


@router.get("/api/purchases")
async def list_purchases(request: Request):
    """List purchases for the current user."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    pool = await get_pool()
    if not pool:
        return {"purchases": []}

    rows = await pool.fetch(
        """SELECT p.id, p.product_id, p.amount, p.currency, p.payment_method,
                  p.status, p.created_at, pr.name as product_name
           FROM purchases p JOIN products pr ON p.product_id = pr.id
           WHERE p.user_id = $1 ORDER BY p.created_at DESC""",
        user_id,
    )
    return {
        "purchases": [
            {
                "id": str(r["id"]),
                "product_id": str(r["product_id"]),
                "product_name": r["product_name"],
                "amount": float(r["amount"]),
                "currency": r["currency"],
                "payment_method": r["payment_method"],
                "status": r["status"],
                "created_at": r["created_at"].isoformat(),
            }
            for r in rows
        ]
    }
