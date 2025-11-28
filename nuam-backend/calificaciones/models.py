from django.db import models
from django.conf import settings

# Nota: JSONField requiere MySQL >= 5.7.8. Si no lo tienes, cambia JSONField por TextField y serializa manualmente.
try:
    from django.db.models import JSONField
except Exception:
    from django.contrib.postgres.fields import JSONField  # fallback (only if postgres)
    # Si usas MySQL antiguo, sustituir JSONField por TextField y usar json.loads/dumps

class Empresa(models.Model):
    rut = models.CharField(max_length=12, db_index=True)
    dv = models.CharField(max_length=1, blank=True, null=True)
    razon_social = models.CharField(max_length=255)
    regimen_tributario = models.CharField(max_length=100, blank=True, null=True)
    capital_propio_tributario = models.BigIntegerField(blank=True, null=True)
    inicio_actividades = models.DateField(blank=True, null=True)
    
    # New fields for Acciones module
    TIPO_SOCIEDAD = (
        ('Ltda', 'Limitada'),
        ('EIRL', 'EIRL'),
        ('SpA', 'SpA'),
        ('SA', 'S.A.'),
    )
    tipo_sociedad = models.CharField(max_length=20, choices=TIPO_SOCIEDAD, blank=True, null=True)
    total_acciones = models.BigIntegerField(blank=True, null=True)
    valor_nominal = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "empresas"

    def __str__(self):
        return f"{self.razon_social} ({self.rut})"


class Propietario(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="propietarios")
    rut = models.CharField(max_length=12, db_index=True)
    dv = models.CharField(max_length=1, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    calidad = models.CharField(max_length=100, blank=True, null=True)  # ej: pleno, nudo-propietario, usufructuario
    porcentaje_participacion = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) # Manual for Ltda/EIRL, calculated for SpA/SA
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "propietarios"
        indexes = [models.Index(fields=["rut"])]

    def __str__(self):
        return f"{self.nombre or self.rut}"


class RegistroEmpresarial(models.Model):
    TIPOS = (
        ("RAI","RAI"),
        ("DDAN","DDAN"),
        ("REX","REX"),
        ("RAP","RAP"),
        ("INR","INR"),
        ("SAC","SAC"),
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="registros")
    tipo = models.CharField(max_length=20, choices=TIPOS)
    saldo_inicial = models.BigIntegerField(blank=True, null=True)
    saldo_final = models.BigIntegerField(blank=True, null=True)
    ejercicio = models.PositiveIntegerField()  # año
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "registros_empresariales"
        unique_together = ("empresa","tipo","ejercicio")


class ArchivoCargado(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name="archivos")
    nombre_archivo = models.CharField(max_length=255)
    ruta = models.CharField(max_length=1024, blank=True, null=True)  # si guardas en FS/Cloud, ruta o URL
    cargado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    cargado_en = models.DateTimeField(auto_now_add=True)
    metadata = JSONField(blank=True, null=True)

    class Meta:
        db_table = "archivos_cargados"


class CalificacionTributaria(models.Model):
    TIPOS = (
        ("retiro","retiro"),
        ("remesa","remesa"),
        ("dividendo","dividendo"),
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="calificaciones")
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name="calificaciones")
    fecha = models.DateField(db_index=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    monto_original = models.BigIntegerField()
    monto_reajustado = models.BigIntegerField(blank=True, null=True)
    imputacion = models.CharField(max_length=50, blank=True, null=True)  # RAI, DDAN, REX, etc.
    detalles = JSONField(blank=True, null=True)  # para campos extra del DJ1948 (por ej columnas detalladas)
    estado = models.CharField(max_length=20, default="vigente", db_index=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    archivo_origen = models.ForeignKey(ArchivoCargado, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "calificaciones_tributarias"
        indexes = [
            models.Index(fields=["empresa","propietario","fecha"]),
            models.Index(fields=["tipo","imputacion"]),
        ]

    def __str__(self):
        return f"{self.tipo} {self.propietario} {self.fecha} ${self.monto_reajustado or self.monto_original}"


class Accion(models.Model):
    TIPO_PROPIEDAD = (
        ('pleno', 'Pleno Propietario'),
        ('nudo', 'Nudo Propietario'),
        ('usufructo', 'Usufructuario'),
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="acciones_emitidas")
    socio = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name="acciones_poseidas")
    cantidad_acciones = models.BigIntegerField()
    valor_nominal = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    fecha_adquisicion = models.DateField(blank=True, null=True)
    tipo_propiedad = models.CharField(max_length=20, choices=TIPO_PROPIEDAD, default='pleno')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "acciones"


class CreditoIDPC(models.Model):
    calificacion = models.ForeignKey(CalificacionTributaria, on_delete=models.CASCADE, related_name="creditos")
    tipo = models.CharField(max_length=100, blank=True, null=True) # ej: con devolución, sin devolución, ISFUT,...
    monto = models.BigIntegerField()
    ejercicio = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "creditos_idpc"


class Auditoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    entidad = models.CharField(max_length=100)  # e.g. "CalificacionTributaria"
    entidad_id = models.BigIntegerField(blank=True, null=True)
    detalle = JSONField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auditoria"
        indexes = [models.Index(fields=["entidad","entidad_id"])]


class Certificado70(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="certificados")
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name="certificados")
    anio_comercial = models.PositiveIntegerField()
    fecha_emision = models.DateField(auto_now_add=True)
    folio = models.PositiveIntegerField(blank=True, null=True)
    
    # JSON Fields for complex data structures (37 columns)
    totales = JSONField(default=dict)  # Summary of totals
    detalles = JSONField(default=list) # List of rows (retiros/dividendos with details)
    
    archivo_pdf = models.CharField(max_length=1024, blank=True, null=True) # Path/URL to generated PDF
    
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "certificados70"
        unique_together = ("empresa", "propietario", "anio_comercial")

    def __str__(self):
        return f"Cert70 {self.empresa} - {self.propietario} ({self.anio_comercial})"
