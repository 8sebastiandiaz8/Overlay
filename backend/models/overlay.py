from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID


@dataclass
class Overlay:
    """Overlay configuration saved from the editor."""

    id: UUID
    user_id: UUID
    name: str
    resolution_w: int = 1920
    resolution_h: int = 1080
    widgets_config: list[Any] = field(default_factory=list)
    is_active: bool = False
    public_url_token: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
