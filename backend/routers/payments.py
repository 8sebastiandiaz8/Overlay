import os

import stripe
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import get_pool
from backend.routers.auth import get_current_user_id

router = APIRouter(tags=["payments"])

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/payments/stripe/create-checkout")
async def create_stripe_checkout(request: Request):
    """Create a Stripe checkout session for a product."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    product_id = body.get("product_id")

    pool = await get_pool()
    if not pool:
        return JSONResponse({"error": "Database unavailable"}, status_code=503)

    product = await pool.fetchrow("SELECT * FROM products WHERE id = $1", product_id)
    if not product:
        return JSONResponse({"error": "Product not found"}, status_code=404)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": product["currency"].lower(),
                    "product_data": {"name": product["name"]},
                    "unit_amount": int(float(product["price"]) * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{request.base_url}store?purchase=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.base_url}store?purchase=cancelled",
            metadata={"user_id": user_id, "product_id": product_id},
        )
        return {"checkout_url": session.url}
    except stripe.StripeError as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.SignatureVerificationError):
        return JSONResponse({"error": "Invalid signature"}, status_code=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        await _activate_purchase(
            user_id=metadata.get("user_id"),
            product_id=metadata.get("product_id"),
            payment_id=session["id"],
            amount=session["amount_total"] / 100,
            method="stripe",
        )

    return {"status": "ok"}


@router.post("/payments/paypal/create-order")
async def create_paypal_order(request: Request):
    """Create a PayPal order (placeholder)."""
    user_id = await get_current_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    # PayPal integration placeholder
    return {"order_id": "PAYPAL_ORDER_PLACEHOLDER", "product_id": body.get("product_id")}


@router.post("/payments/paypal/capture-order")
async def capture_paypal_order(request: Request):
    """Capture a PayPal order (placeholder)."""
    body = await request.json()
    # PayPal capture placeholder
    return {"status": "captured", "order_id": body.get("order_id")}


async def _activate_purchase(
    user_id: str, product_id: str, payment_id: str, amount: float, method: str,
) -> None:
    """Record a completed purchase in the database."""
    pool = await get_pool()
    if not pool:
        return

    await pool.execute(
        """INSERT INTO purchases (user_id, product_id, amount, payment_method, payment_id, status)
           VALUES ($1, $2, $3, $4, $5, 'completed')""",
        user_id, product_id, amount, method, payment_id,
    )
