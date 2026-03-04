import httpx

from backend.config import settings

TWITCH_API_BASE = "https://api.twitch.tv/helix"


async def get_user_info(access_token: str) -> dict:
    """Fetch Twitch user profile information."""
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{TWITCH_API_BASE}/users",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": settings.TWITCH_CLIENT_ID,
            },
        )
        data = res.json()
    return data["data"][0] if data.get("data") else {}


async def get_channel_info(access_token: str, broadcaster_id: str) -> dict:
    """Fetch Twitch channel information."""
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{TWITCH_API_BASE}/channels",
            params={"broadcaster_id": broadcaster_id},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": settings.TWITCH_CLIENT_ID,
            },
        )
        data = res.json()
    return data["data"][0] if data.get("data") else {}


async def subscribe_to_eventsub(
    access_token: str,
    event_type: str,
    broadcaster_id: str,
    callback_url: str,
    secret: str,
) -> dict:
    """Create a Twitch EventSub subscription."""
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{TWITCH_API_BASE}/eventsub/subscriptions",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": settings.TWITCH_CLIENT_ID,
                "Content-Type": "application/json",
            },
            json={
                "type": event_type,
                "version": "1",
                "condition": {"broadcaster_user_id": broadcaster_id},
                "transport": {
                    "method": "webhook",
                    "callback": callback_url,
                    "secret": secret,
                },
            },
        )
    return res.json()
