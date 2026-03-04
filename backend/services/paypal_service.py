import httpx

from backend.config import settings

PAYPAL_BASE = {
    "sandbox": "https://api-m.sandbox.paypal.com",
    "live": "https://api-m.paypal.com",
}


def _get_base_url() -> str:
    """Return the PayPal API base URL based on the configured mode."""
    return PAYPAL_BASE.get(settings.PAYPAL_MODE, PAYPAL_BASE["sandbox"])


async def get_access_token() -> str:
    """Obtain a PayPal API access token using client credentials."""
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{_get_base_url()}/v1/oauth2/token",
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
        )
    return res.json().get("access_token", "")


async def create_order(amount: str, currency: str = "USD") -> dict:
    """Create a PayPal order."""
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{_get_base_url()}/v2/checkout/orders",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {"currency_code": currency, "value": amount},
                }],
            },
        )
    return res.json()


async def capture_order(order_id: str) -> dict:
    """Capture a PayPal order after approval."""
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{_get_base_url()}/v2/checkout/orders/{order_id}/capture",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
    return res.json()
