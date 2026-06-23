import io
from datetime import datetime as _dt

from fastapi import APIRouter
from fastapi.responses import Response
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from backend.models.schemas import ExportPdfRequest

router = APIRouter()


@router.post("/export/pdf")
async def export_pdf(data: ExportPdfRequest):
    """Generate a PDF report from analysis data."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Sabiá - Relatorio de Analise")

    c.setFont("Helvetica", 11)
    y = height - 100
    c.drawString(50, y, f"Task ID: {data.task_id}")
    c.drawString(50, y - 20, f"Formato: {data.format}")

    if data.overlays:
        y -= 50
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Overlays processados:")
        c.setFont("Helvetica", 10)
        for i, overlay in enumerate(data.overlays):
            c.drawString(70, y - 20 * (i + 1), f"  - {overlay}")

    y -= 80
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Resumo da Analise")
    c.setFont("Helvetica", 10)
    y -= 20
    c.drawString(50, y, "Este relatorio foi gerado automaticamente pelo Sabiá.")
    y -= 20
    c.drawString(50, y, "Os dados de遥感 sao processados via Celery workers assincronos.")

    c.setFont("Helvetica", 8)
    c.drawString(50, 30, f"Gerado em: {_dt.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.drawString(width - 100, 30, "Sabiá v0.2.0")

    c.showPage()
    c.save()
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sabia-report.pdf"},
    )
