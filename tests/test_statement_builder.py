from decimal import Decimal

from storefront_statement.models import StatementRequest
from storefront_statement.statement_builder import statement_total


def test_total_counts_only_paid_orders_with_receipts() -> None:
    statement = StatementRequest.model_validate(
        {
            "account_name": "Juniper Supply",
            "currency": "USD",
            "period_start": "2026-08-01T00:00:00Z",
            "period_end": "2026-08-31T23:59:59Z",
            "orders": [
                {
                    "order_number": "ORDER-1042",
                    "placed_at": "2026-08-04T10:00:00Z",
                    "checkout_status": "paid",
                    "fulfillment_status": "delivered",
                    "total": "84.50",
                    "receipt": {"receipt_number": "RCPT-1042", "issued_at": "2026-08-04T10:01:00Z"},
                    "updates": [{"occurred_at": "2026-08-06T09:00:00Z", "message": "Delivered"}],
                },
                {
                    "order_number": "ORDER-1043",
                    "placed_at": "2026-08-08T12:00:00Z",
                    "checkout_status": "pending",
                    "fulfillment_status": "unfulfilled",
                    "total": "25.00",
                    "updates": [],
                },
                {
                    "order_number": "ORDER-1044",
                    "placed_at": "2026-08-09T12:00:00Z",
                    "checkout_status": "paid",
                    "fulfillment_status": "shipped",
                    "total": "10.00",
                    "updates": [],
                },
            ],
        }
    )

    assert statement_total(statement) == Decimal("84.50")

