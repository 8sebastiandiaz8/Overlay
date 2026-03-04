import httpx

from backend.config import settings

KICK_API_BASE = "https://api.kick.com/v1"


async def get_user_info(access_token: str) -> dict:
    """Fetch Kick user profile information."""
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{KICK_API_BASE}/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return res.json()


async def get_channel_info(access_token: str, channel_slug: str) -> dict:
    """Fetch Kick channel information."""
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{KICK_API_BASE}/channels/{channel_slug}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return res.json()
