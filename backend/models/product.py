from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID


@dataclass
class Product:
    """Product available in the widget store."""

    id: UUID
    name: str
    product_type: str
    price: Decimal = Decimal("0.00")
    currency: str = "USD"
    description: Optional[str] = None
    seller_id: Optional[UUID] = None
    preview_url: Optional[str] = None
    download_files: Optional[list[Any]] = None
    tags: Optional[list[str]] = None
    is_published: bool = False
    downloads_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Purchase:
    """Record of a product purchase."""

    id: UUID
    user_id: UUID
    product_id: UUID
    amount: Decimal
    currency: str = "USD"
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
