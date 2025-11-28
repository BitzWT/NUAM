from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from .models import CalificacionTributaria, Empresa, Propietario, Auditoria, Accion
from .serializers import (
    CalificacionTributariaSerializer, EmpresaSerializer, PropietarioSerializer, 
    AuditoriaSerializer, AccionSerializer
)
from core.permissions import IsAdmin, IsAnalista, IsEditor, IsAuditor
from rest_framework.permissions import IsAuthenticated
from .utils import generate_pdf, generate_excel

@api_view(['GET'])
def health(request):
    return Response({'status':'ok'})

class CalificacionTributariaViewSet(viewsets.ModelViewSet):
    queryset = CalificacionTributaria.objects.all().order_by("-fecha")
    serializer_class = CalificacionTributariaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["empresa__razon_social", "propietario__rut"]
    ordering_fields = ["fecha", "monto_original"]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'export_pdf', 'export_excel']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAnalista | IsEditor | IsAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsEditor | IsAdmin]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        headers = ["Fecha", "Empresa", "Propietario", "Tipo", "Monto", "Estado"]
        data = []
        for obj in queryset:
            data.append([
                str(obj.fecha),
                obj.empresa.razon_social,
                obj.propietario.nombre,
                obj.tipo,
                f"${obj.monto_original}",
                obj.estado
            ])
        return generate_pdf("calificaciones", "Reporte de Calificaciones", headers, data)

    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        headers = ["Fecha", "Empresa", "Propietario", "Tipo", "Monto", "Estado"]
        data = []
        for obj in queryset:
            data.append([
                str(obj.fecha),
                obj.empresa.razon_social,
                obj.propietario.nombre,
                obj.tipo,
                obj.monto_original,
                obj.estado
            ])
        return generate_excel("calificaciones", "Calificaciones", headers, data)

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all().order_by("razon_social")
    serializer_class = EmpresaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["razon_social", "rut"]

    @action(detail=True, methods=['get'])
    def acciones(self, request, pk=None):
        """GET /empresas/{id}/acciones/"""
        acciones = Accion.objects.filter(empresa_id=pk)
        serializer = AccionSerializer(acciones, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='socios-con-participacion')
    def socios_con_participacion(self, request, pk=None):
        """GET /empresas/{id}/socios-con-participacion/"""
        empresa = self.get_object()
        propietarios = Propietario.objects.filter(empresa=empresa)
        data = []
        
        total_acciones = empresa.total_acciones or 0
        
        for prop in propietarios:
            # Get shares for this owner
            acciones = Accion.objects.filter(empresa=empresa, socio=prop)
            total_acciones_socio = sum(a.cantidad_acciones for a in acciones)
            
            # Calculate percentage
            porcentaje = 0
            if empresa.tipo_sociedad in ['SpA', 'SA'] and total_acciones > 0:
                porcentaje = (total_acciones_socio / total_acciones) * 100
            else:
                # Use manual percentage if set, otherwise 0
                porcentaje = prop.porcentaje_participacion or 0
            
            data.append({
                "id": prop.id,
                "rut": prop.rut,
                "nombre": prop.nombre,
                "calidad": prop.calidad,
                "cantidad_acciones": total_acciones_socio,
                "porcentaje_participacion": round(porcentaje, 2),
                "tipo_propiedad": acciones[0].tipo_propiedad if acciones else None
            })
            
        return Response(data)

class PropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietario.objects.all().order_by("nombre")
    serializer_class = PropietarioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "rut"]

class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Auditoria.objects.all().order_by("-fecha")
    serializer_class = AuditoriaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["entidad", "accion", "usuario__username"]
    ordering_fields = ["fecha"]
    permission_classes = [IsAdmin | IsAuditor]

    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        headers = ["Fecha", "Usuario", "Acción", "Entidad", "ID"]
        data = []
        for obj in queryset:
            user_str = obj.usuario.username if obj.usuario else "Sistema"
            data.append([
                str(obj.fecha.strftime("%Y-%m-%d %H:%M")),
                user_str,
                obj.accion,
                obj.entidad,
                str(obj.entidad_id)
            ])
        return generate_pdf("auditoria", "Reporte de Auditoría", headers, data)

    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        headers = ["Fecha", "Usuario", "Acción", "Entidad", "ID", "Detalle"]
        data = []
        for obj in queryset:
            user_str = obj.usuario.username if obj.usuario else "Sistema"
            data.append([
                str(obj.fecha.strftime("%Y-%m-%d %H:%M")),
                user_str,
                obj.accion,
                obj.entidad,
                obj.entidad_id,
                str(obj.detalle)
            ])
        return generate_excel("auditoria", "Auditoría", headers, data)

from .models import Certificado70
from .serializers import Certificado70Serializer
from .services.cert70_calculator import Cert70Calculator
from .services.cert70_pdf import Cert70PDFGenerator
from django.shortcuts import get_object_or_404
from django.http import FileResponse

class Certificado70ViewSet(viewsets.ModelViewSet):
    queryset = Certificado70.objects.all().order_by("-fecha_emision")
    serializer_class = Certificado70Serializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def generar(self, request):
        empresa_id = request.data.get('empresa_id')
        propietario_id = request.data.get('propietario_id')
        anio = request.data.get('anio')

        if not all([empresa_id, propietario_id, anio]):
            return Response({"error": "Faltan parámetros (empresa_id, propietario_id, anio)"}, status=400)

        empresa = get_object_or_404(Empresa, pk=empresa_id)
        propietario = get_object_or_404(Propietario, pk=propietario_id)

        # 1. Calculate
        calculator = Cert70Calculator(empresa, propietario, int(anio))
        totales, detalles = calculator.calculate()

        # 2. Save Model
        cert, created = Certificado70.objects.update_or_create(
            empresa=empresa,
            propietario=propietario,
            anio_comercial=anio,
            defaults={
                "totales": totales,
                "detalles": detalles,
                "creado_por": request.user
            }
        )

        # 3. Generate PDF
        generator = Cert70PDFGenerator(cert)
        pdf_path = generator.generate()
        
        cert.archivo_pdf = pdf_path
        cert.save()

        serializer = self.get_serializer(cert)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def descargar(self, request, pk=None):
        cert = self.get_object()
        if not cert.archivo_pdf:
            return Response({"error": "PDF no generado"}, status=404)
        
        return FileResponse(open(cert.archivo_pdf, 'rb'), as_attachment=True, filename=f"Cert70_{cert.id}.pdf")

class AccionViewSet(viewsets.ModelViewSet):
    queryset = Accion.objects.all().order_by("-created_at")
    serializer_class = AccionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["empresa__razon_social", "socio__nombre", "socio__rut"]
