from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID


@dataclass
class UserWidget:
    """Widget instance customized by a user within an overlay."""

    id: UUID
    user_id: UUID
    overlay_id: UUID
    widget_type: str
    name: Optional[str] = None
    config: dict[str, Any] = field(default_factory=dict)
    position_x: int = 0
    position_y: int = 0
    width: int = 300
    height: int = 200
    z_index: int = 1
    is_visible: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
