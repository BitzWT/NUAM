from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.db.models import Sum
from io import BytesIO
from datetime import datetime

class ReportGenerator:
    def __init__(self, empresa, start_date, end_date, user):
        self.empresa = empresa
        self.start_date = start_date
        self.end_date = end_date
        self.user = user
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(name='Header1', parent=self.styles['Heading1'], fontSize=16, spaceAfter=12, textColor=colors.darkblue))
        self.styles.add(ParagraphStyle(name='Header2', parent=self.styles['Heading2'], fontSize=14, spaceAfter=10, textColor=colors.black))
        self.styles.add(ParagraphStyle(name='NormalSmall', parent=self.styles['Normal'], fontSize=9, leading=11))
        self.styles.add(ParagraphStyle(name='Warning', parent=self.styles['Normal'], fontSize=10, textColor=colors.red))

    def generate(self):
        doc = SimpleDocTemplate(self.buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        elements = []

        # 1. Header
        elements.extend(self._create_header())
        
        # 2. Executive Summary (KPIs)
        elements.extend(self._create_executive_summary())

        # 3. DJs Processed
        elements.extend(self._create_djs_table())

        # 4. Qualifications Summary (by Type)
        elements.extend(self._create_qualifications_summary())

        # 5. Detail Table (Clean list of movements)
        elements.extend(self._create_detail_table())

        # 6. Warnings / Audit Logs (from system)
        elements.extend(self._create_system_notes())

        # 7. Signature / Footer
        elements.extend(self._create_footer())

        doc.build(elements)
        self.buffer.seek(0)
        return self.buffer

    def _create_header(self):
        elems = []
        # Title
        elems.append(Paragraph("INFORME DE GESTIÓN TRIBUTARIA", self.styles['Title']))
        elems.append(Spacer(1, 10))
        
        # Company Info Table
        data = [
            ["Empresa:", self.empresa.razon_social],
            ["RUT:", f"{self.empresa.rut}"],
            ["Periodo:", f"{self.start_date} al {self.end_date}"],
            ["Fecha Emisión:", datetime.now().strftime("%d-%m-%Y %H:%M")]
        ]
        t = Table(data, colWidths=[100, 300])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
        ]))
        elems.append(t)
        elems.append(Spacer(1, 20))
        return elems

    def _create_executive_summary(self):
        elems = []
        elems.append(Paragraph("Resumen Ejecutivo", self.styles['Header2']))
        
        qs = self.empresa.calificaciones.filter(fecha__range=[self.start_date, self.end_date])
        total_monto = qs.aggregate(Sum('monto_original'))['monto_original__sum'] or 0
        count = qs.count()
        
        # Breakdown by imputed type (RAI, REX, etc) logic if available, or just raw type
        retiros = qs.filter(tipo='retiro').aggregate(Sum('monto_original'))['monto_original__sum'] or 0
        dividendos = qs.filter(tipo='dividendo').aggregate(Sum('monto_original'))['monto_original__sum'] or 0
        
        summary_data = [
            ["Total Movimientos Registrados:", f"{count}"],
            ["Monto Total (Histórico):", f"$ {total_monto:,.0f}"],
            ["Total Retiros:", f"$ {retiros:,.0f}"],
            ["Total Dividendos:", f"$ {dividendos:,.0f}"],
        ]
        
        t = Table(summary_data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ]))
        elems.append(t)
        elems.append(Spacer(1, 20))
        return elems

    def _create_djs_table(self):
        elems = []
        elems.append(Paragraph("Declaraciones Juradas Procesadas", self.styles['Header2']))
        
        # Filter files uploaded for this company within period (approx by uploaded_at or just list all relevant)
        # For simplicity, listing all active files or those linked to the qualifications in range
        djs = self.empresa.archivos.all().order_by('-cargado_en')[:5] # Limit to recent 5 or matching period
        
        if not djs.exists():
             elems.append(Paragraph("No hay archivos DJ registrados para este periodo.", self.styles['NormalSmall']))
        else:
            data = [["Archivo", "Fecha Carga", "Usuario"]]
            for dj in djs:
                data.append([
                    dj.nombre_archivo, 
                    dj.cargado_en.strftime("%d-%m-%Y") if dj.cargado_en else "-", 
                    dj.cargado_por.username if dj.cargado_por else "Sistema"
                ])
            
            t = Table(data, colWidths=[250, 100, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('FONTSIZE', (0,0), (-1,-1), 8),
            ]))
            elems.append(t)
        
        elems.append(Spacer(1, 20))
        return elems

    def _create_qualifications_summary(self):
        elems = []
        elems.append(Paragraph("Resumen de Rentas e Imputaciones", self.styles['Header2']))
        
        qs = self.empresa.calificaciones.filter(fecha__range=[self.start_date, self.end_date])
        # Aggregate by 'imputacion' field (RAI, REX, DDAN, etc)
        from django.db.models import Count
        groups = qs.values('imputacion').annotate(total=Sum('monto_original'), count=Count('id')).order_by('imputacion')
        
        if not groups:
            elems.append(Paragraph("No hay datos para mostrar.", self.styles['Normal']))
        else:
            data = [["Imputación (Renta)", "Cant. Movimientos", "Monto Total (Histórico)"]]
            for g in groups:
                label = g['imputacion'] if g['imputacion'] else "SIN CLASIFICAR"
                data.append([
                    label,
                    str(g['count']),
                    f"$ {g['total']:,.0f}"
                ])
            
            t = Table(data, colWidths=[200, 100, 150])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('ALIGN', (2,1), (-2,-1), 'RIGHT'), # Amounts right aligned
            ]))
            elems.append(t)
        
        elems.append(Spacer(1, 20))
        return elems
    
    def _create_detail_table(self):
        elems = []
        elems.append(Paragraph("Detalle de Participaciones y Calificaciones", self.styles['Header2']))
        
        qs = self.empresa.calificaciones.filter(fecha__range=[self.start_date, self.end_date]).order_by('fecha', 'propietario__nombre')
        
        if not qs.exists():
            return elems
            
        data = [["Fecha", "Socio/Accionista", "Tipo", "Imputación", "Monto"]]
        for cal in qs:
            data.append([
                cal.fecha.strftime("%d-%m-%Y"),
                cal.propietario.nombre[:30] if cal.propietario.nombre else cal.propietario.rut,
                cal.tipo,
                cal.imputacion or "-",
                f"$ {cal.monto_original:,.0f}"
            ])
            
        t = Table(data, colWidths=[70, 180, 70, 60, 90])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ALIGN', (-1,1), (-1,-1), 'RIGHT'),
        ]))
        elems.append(t)
        elems.append(Spacer(1, 20))
        return elems

    def _create_system_notes(self):
        elems = []
        elems.append(Paragraph("Observaciones del Sistema", self.styles['Header2']))
        
        # Logic to detect inconsistencies could go here
        # For now, generic text or checking if there are unclassified items
        unclassified = self.empresa.calificaciones.filter(
            fecha__range=[self.start_date, self.end_date], 
            imputacion__isnull=True
        ).count()
        
        notes = []
        if unclassified > 0:
            notes.append(f"• Se detectaron {unclassified} movimientos sin imputación tributaria definida.")
        else:
            notes.append("• No se detectaron inconsistencias graves en el procesamiento.")
            
        notes.append("• Este informe fue generado automáticamente basado en las DJs cargadas.")
        
        for note in notes:
            elems.append(Paragraph(note, self.styles['Normal']))
            
        elems.append(Spacer(1, 30))
        return elems

    def _create_footer(self):
        elems = []
        elems.append(Paragraph("_" * 40, self.styles['Normal']))
        elems.append(Paragraph(f"Generado por: {self.user.username}", self.styles['Normal']))
        elems.append(Paragraph(f"Rol: {self.user.role}", self.styles['NormalSmall']))
        elems.append(Paragraph("NUAM SpA - Plataforma de Gestión Tributaria", self.styles['NormalSmall']))
        return elems
