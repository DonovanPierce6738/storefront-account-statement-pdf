import asyncio
import json

from storefront_statement.infrai_pdf import InfraiPdfClient
from storefront_statement.models import StatementRequest
from storefront_statement.statement_service import export_statement


async def main() -> None:
    statement = StatementRequest.model_validate(
        {
            "account_name": "Juniper Supply",
            "currency": "USD",
            "period_start": "2026-08-01T00:00:00Z",
            "period_end": "2026-08-31T23:59:59Z",
            "orders": [{
                "order_number": "ORDER-1042", "placed_at": "2026-08-04T10:00:00Z",
                "checkout_status": "paid", "fulfillment_status": "delivered", "total": "84.50",
                "receipt": {"receipt_number": "RCPT-1042", "issued_at": "2026-08-04T10:01:00Z"},
                "updates": [{"occurred_at": "2026-08-06T09:00:00Z", "message": "Delivered"}],
            }],
        }
    )
    client = InfraiPdfClient()
    try:
        result = await export_statement(statement, client)
        print(json.dumps(result.model_dump(mode="json"), indent=2))
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())

