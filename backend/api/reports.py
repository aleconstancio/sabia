import io
import logging
from datetime import datetime as _dt

from fastapi import APIRouter
from fastapi.responses import Response
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from backend.models.schemas import ExportPdfRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/export/pdf")
async def export_pdf(data: ExportPdfRequest):
    """Generate a PDF report from analysis data."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "SpaceEye - Relatório de Análise")

    c.setFont("Helvetica", 11)
    y = height - 100
    c.drawString(50, y, f"Task: {data.task_id}")
    c.drawString(50, y - 20, f"Formato: {data.format}")

    if data.overlays:
        c.drawString(50, y - 40, f"Overlays: {', '.join(data.overlays)}")

    c.setFont("Helvetica", 8)
    c.drawString(50, 30, f"Gerado em: {_dt.now().strftime('%d/%m/%Y %H:%M')}")

    c.showPage()
    c.save()
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=spaceeye-report.pdf"},
    )
