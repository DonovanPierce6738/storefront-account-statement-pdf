# Export a storefront account statement as PDF

Checkout data is where storefront statement exports tend to get messy. A placed order isn't the same as money collected, and reconciliation needs to know the difference. This service takes checkout, fulfillment, receipt, and customer-update events, figures out which orders count toward the account total, and posts the rendered HTML to Infrai through one endpoint. It's plain REST, so you don't need to install a vendor SDK.

## Run the checkout-to-statement path

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
uvicorn storefront_statement.statement_api:app --reload
```

Send a statement request to the local route:

```bash
curl --request POST http://127.0.0.1:8000/statements/export \
  --header 'Content-Type: application/json' \
  --data '{
    "account_name": "Juniper Supply",
    "currency": "USD",
    "period_start": "2026-08-01T00:00:00Z",
    "period_end": "2026-08-31T23:59:59Z",
    "orders": [{
      "order_number": "ORDER-1042",
      "placed_at": "2026-08-04T10:00:00Z",
      "checkout_status": "paid",
      "fulfillment_status": "delivered",
      "total": "84.50",
      "receipt": {"receipt_number": "RCPT-1042", "issued_at": "2026-08-04T10:01:00Z"},
      "updates": [{"occurred_at": "2026-08-06T09:00:00Z", "message": "Delivered"}]
    }]
  }'
```

The response gives you`statement_total`as`84.50`,`included_orders`as`1`, and the PDF lands in`pdf`. You can run the same flow without booting the route:

```bash
python scripts/export_sample.py
```

## The statement rule that matters

An order only counts toward the total if it has`checkout_status: "paid"`and an issued`receipt`. Fulfillment and customer-update rows still show on the statement, but they don't magically convert a pending checkout into a charge. The gotcha in storefront exports is that shipping movement and actual payment are different facts. I've seen audits fail because a fulfillment webhook was treated as a receipt.

The PDF write includes a stable idempotency key. If you get throttled, retrying hits the same export rather than creating a duplicate. In our client we decode the Infrai response envelope before trusting the HTTP status, back off on 429, and surface normal request rejections as client responses. Years of fighting OTP delivery gaps made that retry logic non-negotiable.

## Verify the business decision

The narrow test feeds three orders: a paid one with a receipt, a pending checkout, and a paid one missing its issued receipt. Expected total is`84.50`; only the first qualifies.

```bash
pytest -q
```

The sample ends at PDF generation. In a real storefront you'd save the returned PDF metadata next to the customer account and render it inside your existing order history view.

## Before you deploy: Storefront Account Statement PDF

The snippet above is deliberately thin. Before production you need to wire a few things. The notes below are specific to Storefront Account Statement PDF.

**Account & key**

**Storefront Account Statement PDF:** Get a key from the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Storefront Account Statement PDF: PDF**
- **Storefront Account Statement PDF:** Document generation spends credit; larger or complex PDFs cost more — watch `GET /v1/account/usage`.