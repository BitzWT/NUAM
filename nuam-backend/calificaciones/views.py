from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from .models import CalificacionTributaria, Empresa, Propietario, Auditoria, Accion, Corredor
from .serializers import (
    CalificacionTributariaSerializer, EmpresaSerializer, PropietarioSerializer, 
    AuditoriaSerializer, AccionSerializer, CorredorSerializer, Certificado70Serializer
)
from core.permissions import IsAdminGeneral, IsAdminTributario, IsAuditorInterno, IsCorredor
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

# ...

class CalificacionTributariaViewSet(viewsets.ModelViewSet):
    serializer_class = CalificacionTributariaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["empresa__razon_social", "propietario__rut"]
    ordering_fields = ["fecha", "monto_original"]

    def get_queryset(self):
        user = self.request.user
        queryset = CalificacionTributaria.objects.all().order_by("-fecha")
        
        if user.role == 'corredor':
            # Filter by companies assigned to the corredor
            try:
                corredor = user.corredor_profile
                queryset = queryset.filter(empresa__in=corredor.empresas.all())
            except Corredor.DoesNotExist:
                queryset = queryset.none()
                
        return queryset
    
    @action(detail=False, methods=['get'], url_path='export_pdf')
    def export_pdf(self, request):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from django.http import HttpResponse

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="calificaciones.pdf"'

        doc = SimpleDocTemplate(response, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        # Header
        elements.append(Paragraph("<b>Reporte de Calificaciones Tributarias</b>", styles['Heading1']))
        elements.append(Spacer(1, 10))
        
        # Use filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # Table Data
        data = [["Fecha", "Empresa", "Propietario", "Tipo", "Monto", "Estado"]]
        
        for cal in queryset:
            data.append([
                Paragraph(str(cal.fecha), styles['Normal']),
                Paragraph(cal.empresa.razon_social or "", styles['Normal']),
                Paragraph(cal.propietario.nombre if cal.propietario else "Sin propietario", styles['Normal']),
                Paragraph(cal.tipo, styles['Normal']),
                Paragraph(f"${cal.monto_original:,.0f}", styles['Normal']),
                Paragraph(cal.estado.capitalize(), styles['Normal']),
            ])
            
        # Table Style
        # Cols: Fecha(80), Empresa(200), Prop(150), Tipo(80), Monto(100), Estado(80) = ~700
        t = Table(data, colWidths=[80, 200, 150, 80, 100, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred), # NUAM Red? 
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(t)
        doc.build(elements)
        return response

    def get_permissions(self):
        # Corredor, Auditor: Read Only
        if self.action in ['list', 'retrieve', 'export_pdf', 'export_excel']:
            permission_classes = [IsAuthenticated & (IsAdminGeneral | IsAdminTributario | IsAuditorInterno | IsCorredor)]
        # Tributario/Admin: Create/Update
        elif self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAdminGeneral | IsAdminTributario]
        # Only Admin General can delete.
        elif self.action == 'destroy':
            permission_classes = [IsAdminGeneral]
        else:
            permission_classes = [IsAdminGeneral]
        return [permission() for permission in permission_classes]

# ...

class EmpresaViewSet(viewsets.ModelViewSet):
    serializer_class = EmpresaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["razon_social", "rut"]

    def get_queryset(self):
        user = self.request.user
        queryset = Empresa.objects.all().order_by("razon_social")
        if user.role == 'corredor':
            try:
                corredor = user.corredor_profile
                queryset = queryset.filter(id__in=corredor.empresas.values_list('id', flat=True))
            except Corredor.DoesNotExist:
                queryset = queryset.none()
        return queryset

    def get_permissions(self):
        # Admin General can do everything.
        # Tributario: Read Only.
        # Corredor: Read Only (Own companies).
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
             return [IsAdminGeneral()]
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated(), (IsAdminGeneral | IsAdminTributario | IsAuditorInterno | IsCorredor)()]
        return [IsAdminGeneral()] 

    def perform_create(self, serializer):
        empresa = serializer.save()
        user = self.request.user
        if user.role == 'corredor':
            # Should not happen as permissions prevent creation, but keeping for safety/admin logic
            try:
                corredor = user.corredor_profile
                corredor.empresas.add(empresa)
            except Corredor.DoesNotExist:
                pass 

    @action(detail=True, methods=['get'], url_path='socios-con-participacion')
    def socios_con_participacion(self, request, pk=None):
        empresa = self.get_object()
        socios = Propietario.objects.filter(empresa=empresa)
        serializer = PropietarioSerializer(socios, many=True)
        return Response(serializer.data)

class PropietarioViewSet(viewsets.ModelViewSet):
    serializer_class = PropietarioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "rut", "empresa__razon_social"]

    def get_queryset(self):
        user = self.request.user
        queryset = Propietario.objects.all().order_by("nombre")
        if user.role == 'corredor':
            try:
                corredor = user.corredor_profile
                queryset = queryset.filter(empresa__in=corredor.empresas.all())
            except Corredor.DoesNotExist:
                queryset = queryset.none()
        return queryset

    def get_permissions(self):
        # Read: All roles
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated(), (IsAdminGeneral | IsAdminTributario | IsAuditorInterno | IsCorredor)()]
        # Write: Only Admin General
        return [IsAdminGeneral()]

# ...

class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditoriaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["entidad", "accion", "usuario__username"]
    ordering_fields = ["fecha"]
    # Only Admin General and Auditor can see logs. Tributario cannot.
    permission_classes = [IsAdminGeneral | IsAuditorInterno]

    def get_queryset(self):
        queryset = Auditoria.objects.all().order_by("-fecha")
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(fecha__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(fecha__date__lte=end_date)
            
        return queryset

    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from django.http import HttpResponse

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="auditoria.pdf"'

        doc = SimpleDocTemplate(response, pagesize=landscape(A4)) # Landscape for more width
        elements = []
        styles = getSampleStyleSheet()
        
        # Header
        elements.append(Paragraph("<b>Reporte de Auditoría</b>", styles['Heading1']))
        elements.append(Spacer(1, 10))
        
        # Data
        logs = self.filter_queryset(self.get_queryset())
        
        # Table Header
        data = [["Fecha", "Usuario", "Acción", "Entidad", "Detalle"]]
        
        # Table Body
        for log in logs:
            date_str = log.fecha.strftime("%Y-%m-%d %H:%M") if log.fecha else ""
            user_str = log.usuario.username if log.usuario else "Sistema"
            # Detalle logic: Use detail if short, or summarize? 
            # Detalle is JSON, use simple string repr or empty if None
            # Truncate detail to avoid huge cells
            detail_str = str(log.detalle)[:50] + "..." if log.detalle else ""
            if len(str(log.detalle)) < 50: detail_str = str(log.detalle) or ""

            data.append([
                Paragraph(date_str, styles['Normal']),
                Paragraph(user_str, styles['Normal']),
                Paragraph(log.accion, styles['Normal']),
                Paragraph(log.entidad, styles['Normal']),
                Paragraph(detail_str, styles['Normal']), # Use Paragraph to wrap text
            ])
            
        # Table Styling
        # Widths: A4 Landscape is ~840pts.
        # 100, 100, 80, 100, 300 = 680. Fits. 
        t = Table(data, colWidths=[110, 100, 80, 120, 300]) 
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(t)
        doc.build(elements)
        return response

    @action(detail=False, methods=['get'])
    def export_xlsx(self, request):
        import pandas as pd
        from django.http import HttpResponse

        logs = self.filter_queryset(self.get_queryset())
        data = []
        for log in logs:
            data.append({
                "Fecha": log.fecha.strftime("%Y-%m-%d %H:%M") if log.fecha else "",
                "Usuario": log.usuario.username if log.usuario else "Sistema",
                "Accion": log.accion,
                "Entidad": log.entidad,
                "Detalle": log.detalle
            })
        
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="auditoria.xlsx"'
        df.to_excel(response, index=False)
        return response

# ...

class Certificado70ViewSet(viewsets.ModelViewSet):
    serializer_class = Certificado70Serializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Certificado70.objects.all().order_by("-fecha_emision")
        if user.role == 'corredor':
            try:
                corredor = user.corredor_profile
                queryset = queryset.filter(empresa__in=corredor.empresas.all())
            except Corredor.DoesNotExist:
                queryset = queryset.none()
        return queryset

    @action(detail=False, methods=['post'], url_path='generar')
    def generar(self, request):
        empresa_id = request.data.get('empresa_id')
        propietario_id = request.data.get('propietario_id')
        anio = request.data.get('anio')

        if not empresa_id or not anio:
            return Response({"error": "Faltan datos: empresa_id, anio"}, status=400)

        try:
            empresa = Empresa.objects.get(id=empresa_id)
        except Empresa.DoesNotExist:
            return Response({"error": "Empresa no encontrada"}, status=404)

        # Logic to aggregate data and create Certificates 70 per partner
        # 1. Get partners (All or Single)
        if propietario_id:
            socios = Propietario.objects.filter(empresa=empresa, id=propietario_id)
        else:
            socios = Propietario.objects.filter(empresa=empresa)
        
        created_count = 0
        last_cert = None
        
        for socio in socios:
            # 2. Get tax movements for this partner in that year
            calificaciones = CalificacionTributaria.objects.filter(
                empresa=empresa,
                propietario=socio,
                fecha__year=anio,
                estado='vigente'
            )
            
            # Even if no movements, sometimes certificates are needed with 0 values? 
            # For now, skip if empty to avoid noise, unless requested explicitly.
            if not calificaciones.exists():
                continue

            # 3. Calculate Totals and Details
            totales = {
                'monto_historico': 0, 'monto_actualizado': 0,
                'rai': 0, 'ddan': 0, 'rex': 0, 'inr': 0, 'sac': 0,
                'credito_con_dev': 0, 'credito_sin_dev': 0, 'credito_restitucion': 0,
                'isfut': 0, 'otros_creditos': 0
            }
            
            detalles_list = []
            
            for cal in calificaciones:
                # Map imputation string to key (naive)
                imputacion = (cal.imputacion or "").lower()
                
                # Update Totals
                totales['monto_historico'] += cal.monto_original
                totales['monto_actualizado'] += (cal.monto_reajustado or cal.monto_original)
                
                if 'rai' in imputacion: totals_key = 'rai'
                elif 'rex' in imputacion: totals_key = 'rex'
                elif 'ddan' in imputacion: totals_key = 'ddan'
                else: totals_key = None
                
                if totals_key:
                    totales[totals_key] += (cal.monto_reajustado or cal.monto_original)
                
                detalles_list.append({
                    "fecha": cal.fecha.strftime("%Y-%m-%d"),
                    "tipo": cal.tipo,
                    "monto_historico": cal.monto_original,
                    "monto_actualizado": (cal.monto_reajustado or cal.monto_original),
                    "imputacion": cal.imputacion
                })

            # 4. Create or Update Cert70
            cert, created = Certificado70.objects.update_or_create(
                empresa=empresa,
                propietario=socio,
                anio_comercial=anio,
                defaults={
                    'folio': 100 + created_count + 1, # Dummy folio logic
                    'totales': totales,
                    'detalles': detalles_list,
                    'creado_por': request.user
                }
            )
            created_count += 1
            last_cert = cert

        if created_count == 1 and last_cert:
             # Return the single object structure if only 1 generated (for frontend download link)
             serializer = self.get_serializer(last_cert)
             return Response(serializer.data)

        return Response({"message": f"Se han generado {created_count} certificados para {empresa.razon_social}", "count": created_count})

    def get_permissions(self):
        # View: All roles
        if self.action in ['list', 'retrieve', 'descargar']:
             permission_classes = [IsAuthenticated & (IsAdminGeneral | IsAdminTributario | IsAuditorInterno | IsCorredor)]
        # Generate: Admin/Tributario
        elif self.action == 'generar':
             permission_classes = [IsAdminGeneral | IsAdminTributario]
        else:
             permission_classes = [IsAdminGeneral]
        return [permission() for permission in permission_classes]

# ...

class AccionViewSet(viewsets.ModelViewSet):
    serializer_class = AccionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["empresa__razon_social", "socio__nombre", "socio__rut"]

    def get_queryset(self):
        user = self.request.user
        queryset = Accion.objects.all().order_by("-created_at")
        if user.role == 'corredor':
            try:
                corredor = user.corredor_profile
                queryset = queryset.filter(empresa__in=corredor.empresas.all())
            except Corredor.DoesNotExist:
                queryset = queryset.none()
        return queryset

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
             return [IsAuthenticated(), (IsAdminGeneral | IsAdminTributario | IsAuditorInterno | IsCorredor)()]
        return [IsAdminGeneral()] # Only Admin manages equity/shares

# ...

class CorredorViewSet(viewsets.ModelViewSet):
    queryset = Corredor.objects.all()
    serializer_class = CorredorSerializer
    permission_classes = [IsAdminGeneral] # Only Admin General manages corredores

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        try:
            corredor = request.user.corredor_profile
            serializer = self.get_serializer(corredor)
            return Response(serializer.data)
        except Corredor.DoesNotExist:
            return Response({"error": "Perfil de corredor no encontrado"}, status=404)

@api_view(['GET'])
def health(request):
    return Response({"status": "ok", "service": "nuam-backend"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Returns statistics for the main dashboard.
    """
    user = request.user
    # Only internal roles should access full stats (Admin, Tributario, Auditor)
    if user.role not in ['admin', 'tributario', 'auditor'] and not user.is_superuser:
        return Response({"error": "Unauthorized"}, status=403)

    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    last_7_days = now - timedelta(days=7)

    # 1. Calificaciones Vigentes
    calificaciones_vigentes = CalificacionTributaria.objects.filter(estado__in=['vigente', 'aprobada', 'pendiente']).count()

    # 2. Empresas Activas (Total)
    empresas_count = Empresa.objects.count()

    # 3. Auditorias Recientes (Last 7 days)
    auditorias_recent_count = Auditoria.objects.filter(fecha__gte=last_7_days).count()

    # 4. Recent Activity (Last 5)
    recent_activity = Auditoria.objects.select_related('usuario').order_by('-fecha')[:5]
    activity_data = []
    for log in recent_activity:
        activity_data.append({
            "id": log.id,
            "mensaje": f"{log.accion} en {log.entidad}",
            "usuario": log.usuario.username if log.usuario else "Sistema",
            "fecha": log.fecha.isoformat(),
            "detalles": log.descripcion or ""
        })

    data = {
        "calificaciones_vigentes": calificaciones_vigentes,
        "empresas_activas": empresas_count,
        "auditorias_recientes": auditorias_recent_count,
        "actividad_reciente": activity_data
    }
    return Response(data)

class InformeGestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .services.report_generator import ReportGenerator
        from django.http import FileResponse
        from datetime import datetime
        
        empresa_id = request.query_params.get('empresa_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not all([empresa_id, start_date, end_date]):
            return Response({"error": "Faltan parámetros: empresa_id, start_date, end_date"}, status=400)

        try:
            empresa = Empresa.objects.get(id=empresa_id)
        except Empresa.DoesNotExist:
            return Response({"error": "Empresa no encontrada"}, status=404)

        # Permission Check: Corredor can only see own companies
        if request.user.role == 'corredor':
            try:
                if not request.user.corredor_profile.empresas.filter(id=empresa.id).exists():
                     return Response({"error": "No tienes permiso para ver esta empresa"}, status=403)
            except:
                return Response({"error": "Perfil corredor inválido"}, status=403)

        pdf_buffer = ReportGenerator(empresa, start_date, end_date, request.user).generate()
        
        filename = f"Informe_Gestion_{empresa.rut}_{start_date}_{end_date}.pdf"
        response = FileResponse(pdf_buffer, as_attachment=True, filename=filename)
        return response
