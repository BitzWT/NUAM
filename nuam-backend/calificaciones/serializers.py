from rest_framework import serializers
from .models import (
    Empresa, Propietario, RegistroEmpresarial, ArchivoCargado,
    CalificacionTributaria, Accion, CreditoIDPC, Auditoria, Certificado70, Corredor
)
from django.db.models import Sum
from .validators import validate_rut, validate_positive

class EmpresaSerializer(serializers.ModelSerializer):
    rut = serializers.CharField(validators=[validate_rut])
    capital_propio_tributario = serializers.IntegerField(validators=[validate_positive], required=False, allow_null=True)
    total_acciones = serializers.IntegerField(validators=[validate_positive], required=False, allow_null=True)
    valor_nominal = serializers.DecimalField(max_digits=15, decimal_places=2, validators=[validate_positive], required=False, allow_null=True)

    class Meta:
        model = Empresa
        fields = "__all__"

class PropietarioSerializer(serializers.ModelSerializer):
    rut = serializers.CharField(validators=[validate_rut])
    porcentaje_participacion = serializers.DecimalField(max_digits=5, decimal_places=2, validators=[validate_positive], required=False, allow_null=True)

    class Meta:
        model = Propietario
        fields = "__all__"

    def validate_porcentaje_participacion(self, value):
        if value and value > 100:
            raise serializers.ValidationError("El porcentaje no puede ser mayor a 100.")
        return value

class AccionSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.ReadOnlyField(source='empresa.razon_social')
    socio_nombre = serializers.ReadOnlyField(source='socio.nombre')
    cantidad_acciones = serializers.IntegerField(validators=[validate_positive])
    valor_nominal = serializers.DecimalField(max_digits=15, decimal_places=2, validators=[validate_positive], required=False, allow_null=True)

    class Meta:
        model = Accion
        fields = "__all__"

    def validate(self, data):
        empresa = data.get('empresa')
        cantidad = data.get('cantidad_acciones')
        
        # Only validate for SpA/SA
        if empresa.tipo_sociedad not in ['SpA', 'SA']:
            return data

        total_empresa = empresa.total_acciones or 0
        
        # Calculate existing assigned shares
        # Exclude current instance if updating
        query = Accion.objects.filter(empresa=empresa)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
            
        existing = query.aggregate(Sum('cantidad_acciones'))['cantidad_acciones__sum'] or 0
        
        if existing + cantidad > total_empresa:
            disponible = total_empresa - existing
            raise serializers.ValidationError(
                f"No hay suficientes acciones disponibles. Total: {total_empresa}, "
                f"Asignadas: {existing}, Disponibles: {disponible}, Intento: {cantidad}"
            )
        
        return data

class RegistroEmpresarialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroEmpresarial
        fields = "__all__"

class ArchivoCargadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivoCargado
        fields = "__all__"

class CalificacionTributariaSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.ReadOnlyField(source='empresa.razon_social')
    propietario_nombre = serializers.ReadOnlyField(source='propietario.nombre')
    monto_original = serializers.IntegerField(validators=[validate_positive])
    monto_reajustado = serializers.IntegerField(validators=[validate_positive], required=False, allow_null=True)

    class Meta:
        model = CalificacionTributaria
        fields = "__all__"

class CreditoIDPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditoIDPC
        fields = "__all__"

class AuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auditoria
        fields = "__all__"

class Certificado70Serializer(serializers.ModelSerializer):
    empresa_nombre = serializers.ReadOnlyField(source='empresa.razon_social')
    propietario_nombre = serializers.ReadOnlyField(source='propietario.nombre')
    
    class Meta:
        model = Certificado70
        fields = "__all__"

class CorredorSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = Corredor
        fields = "__all__"