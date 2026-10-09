from hashlib import sha256

from .infrai_pdf import InfraiPdfClient
from .models import StatementExport, StatementRequest
from .statement_builder import is_statement_charge, render_statement_html, statement_total


async def export_statement(statement: StatementRequest, client: InfraiPdfClient) -> StatementExport:
    if statement.period_end < statement.period_start:
        raise ValueError("period_end must be on or after period_start")
    html = render_statement_html(statement)
    pdf = await client.generate(
        html,
        idempotency_key=f"statement-{sha256(html.encode()).hexdigest()}",
    )
    return StatementExport(
        statement_total=statement_total(statement),
        included_orders=sum(is_statement_charge(order) for order in statement.orders),
        pdf=pdf,
    )
