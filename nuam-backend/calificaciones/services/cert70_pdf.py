import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from django.conf import settings

class Cert70PDFGenerator:
    def __init__(self, certificado):
        self.certificado = certificado
        self.output_dir = os.path.join(settings.MEDIA_ROOT, 'certificados')
        os.makedirs(self.output_dir, exist_ok=True)
        self.filename = f"Cert70_{self.certificado.id}.pdf"
        self.filepath = os.path.join(self.output_dir, self.filename)

    def generate(self):
        # Use landscape for better table fit
        doc = SimpleDocTemplate(self.filepath, pagesize=landscape(A4),
                                rightMargin=1*cm, leftMargin=1*cm,
                                topMargin=1*cm, bottomMargin=1*cm)
        
        elements = []
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1, fontSize=14)
        style_normal = styles['Normal']
        style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

        # --- SECCIÓN 1: Identificación ---
        folio_str = str(self.certificado.folio) if self.certificado.folio else "PROVISORIO"
        elements.append(Paragraph(f"Certificado N°70 (Folio: {folio_str}) – Retiros, Remesas o Dividendos", style_title))
        elements.append(Spacer(1, 0.2*cm))
        
        header_data = [
            [f"Año Comercial: {self.certificado.anio_comercial}", f"Fecha Emisión: {self.certificado.fecha_emision.strftime('%d-%m-%Y')}"],
            ["Resolución Exenta SII N°98", "Layout Anexo 3"]
        ]
        t_header = Table(header_data, colWidths=[14*cm, 14*cm])
        t_header.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ]))
        elements.append(t_header)
        elements.append(Spacer(1, 0.5*cm))

        # --- SECCIÓN 2: Datos de la Empresa ---
        emp = self.certificado.empresa
        emp_data = [
            [Paragraph("<b>SECCIÓN 2: DATOS DE LA EMPRESA</b>", style_normal)],
            [f"RUT: {emp.rut}", f"Razón Social: {emp.razon_social}"],
            [f"Régimen: {emp.regimen_tributario or 'N/A'}", f"Comuna: -"], # Comuna not in model yet
        ]
        t_emp = Table(emp_data, colWidths=[14*cm, 14*cm])
        t_emp.setStyle(TableStyle([
            ('SPAN', (0,0), (1,0)),
            ('BACKGROUND', (0,0), (1,0), colors.orange),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(t_emp)
        elements.append(Spacer(1, 0.5*cm))

        # --- SECCIÓN 3: Datos del Socio ---
        prop = self.certificado.propietario
        pct_str = f"{prop.porcentaje_participacion}%" if prop.porcentaje_participacion else "-"
        prop_data = [
            [Paragraph("<b>SECCIÓN 3: DATOS DEL SOCIO / ACCIONISTA</b>", style_normal)],
            [f"RUT: {prop.rut}", f"Nombre: {prop.nombre}"],
            [f"Calidad: {prop.calidad or 'N/A'}", f"% Participación: {pct_str}"],
        ]
        t_prop = Table(prop_data, colWidths=[14*cm, 14*cm])
        t_prop.setStyle(TableStyle([
            ('SPAN', (0,0), (1,0)),
            ('BACKGROUND', (0,0), (1,0), colors.lightgreen),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(t_prop)
        elements.append(Spacer(1, 0.5*cm))

        # --- SECCIÓN 4: Detalle de Movimientos ---
        elements.append(Paragraph("<b>SECCIÓN 4: DETALLE DE MOVIMIENTOS</b>", style_bold))
        elements.append(Spacer(1, 0.2*cm))

        # Table Headers
        # Grouped headers
        headers_top = ["Movimiento", "", "", "", "Imputación", "", "", "", "", "Créditos IDPC", "", "", "Otros"]
        headers_sub = [
            "Fecha", "Tipo", "Monto Hist", "Monto Act", 
            "RAI", "DDAN", "REX", "INR", "SAC", 
            "C.Con Dev", "C.Sin Dev", "Restit.", "ISFUT/Otros"
        ]
        
        data = [headers_top, headers_sub]

        detalles = self.certificado.detalles
        if not detalles:
             data.append(["Sin movimientos", "", "", "", "", "", "", "", "", "", "", "", ""])
        else:
            for d in detalles:
                row = [
                    str(d.get("fecha", "")),
                    str(d.get("tipo", "")),
                    f"{d.get('monto_historico', 0):,}",
                    f"{d.get('monto_actualizado', 0):,}",
                    f"{d.get('rai', 0):,}",
                    f"{d.get('ddan', 0):,}",
                    f"{d.get('rex', 0):,}",
                    f"{d.get('inr', 0):,}",
                    f"{d.get('sac', 0):,}",
                    f"{d.get('credito_con_dev', 0):,}",
                    f"{d.get('credito_sin_dev', 0):,}",
                    f"{d.get('credito_restitucion', 0):,}",
                    f"{d.get('isfut', 0) + d.get('otros_creditos', 0):,}"
                ]
                data.append(row)

        # Totals Row
        totales = self.certificado.totales
        row_total = [
            "TOTALES", "", 
            f"{totales.get('monto_historico', 0):,}",
            f"{totales.get('monto_actualizado', 0):,}",
            f"{totales.get('rai', 0):,}",
            f"{totales.get('ddan', 0):,}",
            f"{totales.get('rex', 0):,}",
            f"{totales.get('inr', 0):,}",
            f"{totales.get('sac', 0):,}",
            f"{totales.get('credito_con_dev', 0):,}",
            f"{totales.get('credito_sin_dev', 0):,}",
            f"{totales.get('credito_restitucion', 0):,}",
            f"{totales.get('isfut', 0) + totales.get('otros_creditos', 0):,}"
        ]
        data.append(row_total)

        # Column Widths (total ~28cm)
        cw = [2.2*cm, 2*cm, 2.2*cm, 2.2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2.5*cm]
        
        t_det = Table(data, colWidths=cw, repeatRows=2)
        t_det.setStyle(TableStyle([
            ('SPAN', (0,0), (3,0)), # Movimiento
            ('SPAN', (4,0), (8,0)), # Imputacion
            ('SPAN', (9,0), (11,0)), # Creditos
            ('SPAN', (12,0), (12,0)), # Otros
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,1), colors.lightgrey), # Headers background
            ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'), # Totals bold
            ('BACKGROUND', (0,-1), (-1,-1), colors.whitesmoke),
        ]))
        elements.append(t_det)
        elements.append(Spacer(1, 1*cm))

        # --- SECCIÓN 5: Observaciones ---
        elements.append(Paragraph("<b>SECCIÓN 5: OBSERVACIONES</b>", style_bold))
        elements.append(Paragraph("El presente certificado se emite en virtud de lo dispuesto en la Resolución Exenta SII N°98 y debe ser utilizado por el contribuyente para su declaración anual de impuestos.", style_normal))
        elements.append(Spacer(1, 2*cm))

        # --- SECCIÓN 6: Firma ---
        elements.append(Paragraph("__________________________________", style_normal))
        elements.append(Paragraph("Firma Representante Legal", style_normal))
        elements.append(Paragraph(f"{emp.razon_social}", style_normal))
        elements.append(Paragraph(f"RUT: {emp.rut}", style_normal))

        doc.build(elements)
        return self.filepath
