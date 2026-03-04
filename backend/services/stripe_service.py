import stripe

from backend.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(
    product_name: str,
    amount_cents: int,
    currency: str,
    success_url: str,
    cancel_url: str,
    metadata: dict | None = None,
) -> stripe.checkout.Session:
    """Create a Stripe checkout session."""
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": currency.lower(),
                "product_data": {"name": product_name},
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata or {},
    )


def verify_webhook(payload: bytes, signature: str) -> dict:
    """Verify and construct a Stripe webhook event."""
    return stripe.Webhook.construct_event(
        payload, signature, settings.STRIPE_WEBHOOK_SECRET,
    )
