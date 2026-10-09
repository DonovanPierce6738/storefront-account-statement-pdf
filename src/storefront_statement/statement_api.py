from fastapi import FastAPI, HTTPException

from .infrai_pdf import InfraiError, InfraiPdfClient
from .models import StatementExport, StatementRequest
from .statement_service import export_statement

app = FastAPI(title="Storefront statement exporter")


@app.post("/statements/export", response_model=StatementExport)
async def create_statement(statement: StatementRequest) -> StatementExport:
    client = InfraiPdfClient()
    try:
        return await export_statement(statement, client)
    except InfraiError as exc:
        status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(status_code=status, detail=exc.detail) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        await client.close()

