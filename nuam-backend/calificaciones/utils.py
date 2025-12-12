import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook
from django.http import HttpResponse

def generate_pdf(filename, title, headers, data):
    """
    Generates a PDF response.
    headers: list of strings
    data: list of lists (rows)
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 20))

    # Table Data
    table_data = [headers] + data
    
    # Create Table
    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

def generate_excel(filename, title, headers, data):
    """
    Generates an Excel response.
    headers: list of strings
    data: list of lists (rows)
    """
    wb = Workbook()
    ws = wb.active
    ws.title = title[:30] # Excel sheet name limit

    ws.append(headers)
    for row in data:
        # Convert non-serializable objects to string if necessary
        cleaned_row = [str(item) if item is not None else "" for item in row]
        ws.append(cleaned_row)

    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    wb.save(response)
    return response

def generate_error_report(filename, error_context):
    """
    Generates an Error Report PDF.
    error_context: dict with keys 'line', 'reason', 'criterio', 'usuario', 'timestamp'
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("INFORME DE ERROR DE CARGA - NUAM", styles['Title']))
    elements.append(Spacer(1, 20))

    # Error Details
    data = [
        ["Campo", "Detalle"],
        ["Usuario", error_context.get('usuario', 'Sistema')],
        ["Fecha/Hora", error_context.get('timestamp', '')],
        ["Archivo", error_context.get('archivo', 'Desconocido')],
        ["Línea Fallida", str(error_context.get('line', 'N/A'))],
        ["Motivo del Error", error_context.get('reason', 'Desconocido')],
        ["Criterio Incumplido", error_context.get('criterio', 'N/A')],
    ]

    t = Table(data, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 5), (1, 5), colors.mistyrose), # Highlight reason
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Este documento certifica que la carga ha sido rechazada por incumplimiento de validaciones tributarias.", styles['Normal']))

    doc.build(elements)
    
    buffer.seek(0)
    # We return bytes, not response, because this might be saved to disk
    return buffer.getvalue()
