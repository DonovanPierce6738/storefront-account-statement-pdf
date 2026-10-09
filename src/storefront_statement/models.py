from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class CheckoutStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELED = "canceled"


class FulfillmentStatus(str, Enum):
    UNFULFILLED = "unfulfilled"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


class Receipt(BaseModel):
    receipt_number: str
    issued_at: datetime


class CustomerUpdate(BaseModel):
    occurred_at: datetime
    message: str


class StatementOrder(BaseModel):
    order_number: str
    placed_at: datetime
    checkout_status: CheckoutStatus
    fulfillment_status: FulfillmentStatus
    total: Decimal = Field(ge=0)
    receipt: Receipt | None = None
    updates: list[CustomerUpdate] = Field(default_factory=list)


class StatementRequest(BaseModel):
    account_name: str
    currency: str = Field(min_length=3, max_length=3)
    period_start: datetime
    period_end: datetime
    orders: list[StatementOrder]


class StatementExport(BaseModel):
    statement_total: Decimal
    included_orders: int
    pdf: dict[str, object]

