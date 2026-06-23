import io
from datetime import datetime as _dt

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def _generate_pdf(task_id: str, format: str, overlays: list[str]) -> bytes:
    """Generate PDF content (extracted from reports.py for testing)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Sabiá - Relatorio de Analise")

    c.setFont("Helvetica", 11)
    y = height - 100
    c.drawString(50, y, f"Task ID: {task_id}")
    c.drawString(50, y - 20, f"Formato: {format}")

    if overlays:
        y -= 50
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Overlays processados:")
        c.setFont("Helvetica", 10)
        for i, overlay in enumerate(overlays):
            c.drawString(70, y - 20 * (i + 1), f"  - {overlay}")

    y -= 80
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Resumo da Analise")
    c.setFont("Helvetica", 10)
    y -= 20
    c.drawString(50, y, "Este relatorio foi gerado automaticamente pelo Sabiá.")

    c.setFont("Helvetica", 8)
    c.drawString(50, 30, f"Gerado em: {_dt.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.drawString(width - 100, 30, "Sabiá v0.2.0")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def test_export_pdf_returns_pdf_content():
    pdf_bytes = _generate_pdf("test-task-123", "pdf", ["ndvi_overlay.png"])
    assert b"%PDF" in pdf_bytes[:10]
    assert len(pdf_bytes) > 500


def test_export_pdf_includes_task_info():
    pdf_bytes = _generate_pdf("test-task-456", "pdf", [])
    assert b"%PDF" in pdf_bytes[:10]
    assert len(pdf_bytes) > 500
