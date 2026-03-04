from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class User:
    """User model representing a streamer."""

    id: UUID
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    plan: str = "free"
    twitch_id: Optional[str] = None
    kick_id: Optional[str] = None
    twitch_access_token: Optional[str] = None
    twitch_refresh_token: Optional[str] = None
    kick_access_token: Optional[str] = None
    kick_refresh_token: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
