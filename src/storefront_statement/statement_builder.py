from decimal import Decimal
from html import escape

from .models import CheckoutStatus, StatementOrder, StatementRequest


def is_statement_charge(order: StatementOrder) -> bool:
    return order.checkout_status == CheckoutStatus.PAID and order.receipt is not None


def statement_total(statement: StatementRequest) -> Decimal:
    return sum(
        (order.total for order in statement.orders if is_statement_charge(order)),
        start=Decimal("0"),
    )


def render_statement_html(statement: StatementRequest) -> str:
    rows = "".join(_order_row(order) for order in statement.orders)
    total = statement_total(statement)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
body {{ font-family: sans-serif; color: #202124; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 8px; border-bottom: 1px solid #ddd; text-align: left; }}
.amount {{ text-align: right; }}
</style></head><body>
<h1>Account statement</h1>
<p>{escape(statement.account_name)} | {statement.period_start.date()} to {statement.period_end.date()}</p>
<table><thead><tr><th>Order</th><th>Checkout</th><th>Fulfillment</th><th>Receipt</th><th class="amount">Amount</th></tr></thead>
<tbody>{rows}</tbody></table>
<h2>Total: {escape(statement.currency.upper())} {total:.2f}</h2>
</body></html>"""


def _order_row(order: StatementOrder) -> str:
    receipt = order.receipt.receipt_number if order.receipt else "Pending"
    updates = " / ".join(update.message for update in order.updates) or "No updates"
    amount = f"{order.total:.2f}" if is_statement_charge(order) else "-"
    return (
        f"<tr><td>{escape(order.order_number)}<br><small>{escape(updates)}</small></td>"
        f"<td>{order.checkout_status.value}</td>"
        f"<td>{order.fulfillment_status.value}</td>"
        f"<td>{escape(receipt)}</td><td class=\"amount\">{amount}</td></tr>"
    )

