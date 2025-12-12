import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Empresa, Propietario, CalificacionTributaria
from .services.pdf_parser import PDFParser
import os
import tempfile

class BulkUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=400)

        try:
            # Determine file type and read
            if file_obj.name.endswith('.csv'):
                df = pd.read_csv(file_obj)
            else:
                df = pd.read_excel(file_obj)
        except Exception as e:
            return Response({"error": f"Error reading file: {str(e)}"}, status=400)

        required_columns = [
            'rut_empresa', 'razon_social', 
            'rut_propietario', 'nombre_propietario', 
            'fecha', 'tipo_calificacion', 'monto'
        ]
        
        # Check columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            return Response({"error": f"Missing columns: {', '.join(missing_cols)}"}, status=400)

        results = {
            "created": 0,
            "errors": []
        }

        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    # 1. Empresa
                    empresa, _ = Empresa.objects.get_or_create(
                        rut=str(row['rut_empresa']),
                        defaults={'razon_social': str(row['razon_social'])}
                    )

                    # 2. Propietario
                    propietario, _ = Propietario.objects.get_or_create(
                        rut=str(row['rut_propietario']),
                        empresa=empresa,
                        defaults={'nombre': str(row['nombre_propietario'])}
                    )

                    # 3. Calificacion
                    CalificacionTributaria.objects.create(
                        empresa=empresa,
                        propietario=propietario,
                        fecha=pd.to_datetime(row['fecha']).date(),
                        tipo=str(row['tipo_calificacion']),
                        monto_original=int(row['monto']),
                        estado=row.get('estado', 'pendiente')
                    )
                    results["created"] += 1

            except Exception as e:
                results["errors"].append(f"Row {index + 2}: {str(e)}")

        return Response(results)

class PDFUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=400)

        if not file_obj.name.lower().endswith('.pdf'):
            return Response({"error": "File must be a PDF"}, status=400)

        tmp_path = None
        try:
            # 1. Save to temp first to extract metadata
            import time
            from django.conf import settings
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in file_obj.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            # 2. Extract Metadata (Basic Parse)
            parser = PDFParser(tmp_path)
            data = parser.parse_data()
            
            rut_empresa = data.get('rut_empresa') or 'unknown_rut'
            fecha_str = data.get('fecha') or 'unknown_date'
            year = 'unknown_year'
            if fecha_str != 'unknown_date':
                try:
                    year = pd.to_datetime(fecha_str, dayfirst=True).year
                except:
                    pass
            
            # 3. Define Permanent Path
            storage_dir = os.path.join(settings.MEDIA_ROOT, 'djs', str(rut_empresa), str(year))
            os.makedirs(storage_dir, exist_ok=True)
            
            timestamp = int(time.time())
            final_filename = f"DJ1948_{timestamp}.pdf"
            final_path = os.path.join(storage_dir, final_filename)
            
            # Move file
            import shutil
            shutil.move(tmp_path, final_path)
            tmp_path = None # Moved, so temp is gone (or we should have copied)
            # shutil.move removes source if on same filesystem, usually.
            
            # 4. Create ArchivoCargado Record
            from .models import ArchivoCargado, Empresa
            
            empresa_obj = Empresa.objects.filter(rut=rut_empresa).first()
            
            archivo = ArchivoCargado.objects.create(
                empresa=empresa_obj,
                nombre_archivo=final_filename,
                ruta=final_path,
                cargado_por=request.user,
                metadata=data
            )

            return Response(data)

        except Exception as e:
            # Error Handling: Generate Error Report
            import datetime
            from .utils import generate_error_report
            
            timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_context = {
                'line': 'Unknown',
                'reason': str(e),
                'criterio': 'Error de Procesamiento',
                'usuario': request.user.username,
                'timestamp': timestamp_str,
                'archivo': file_obj.name
            }
            
            # Generate (and logically save) report
            pdf_bytes = generate_error_report("error_report", error_context)
            
            # Cleanup temp if it still exists
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
            
            return Response({
                "error": f"Error processing PDF: {str(e)}",
                "error_report_generated": True,
                "details": error_context
            }, status=400)

class BulkCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.get('data')
        if not data:
            return Response({"error": "No data provided"}, status=400)

        results = {
            "created": 0,
            "errors": []
        }

        # Expecting data to be a list of objects similar to what PDFParser returns, 
        # but flattened or structured. 
        # Actually, PDFParser returns {rut_empresa, rut_propietario, calificaciones: []}
        # We need to iterate over qualifications.
        
        # Let's assume the frontend sends a list of qualifications with company/owner info attached
        # OR the frontend sends the exact structure from PDFParser and we handle it.
        # Let's support the structure: { rut_empresa, rut_propietario, calificaciones: [...] }
        
        try:
            rut_empresa = data.get('rut_empresa')
            rut_propietario = data.get('rut_propietario')
            calificaciones = data.get('calificaciones', [])
            
            # Optional: Razon Social and Nombre Propietario might be missing from PDF or edited by user
            razon_social = data.get('razon_social', 'Empresa sin nombre')
            nombre_propietario = data.get('nombre_propietario', 'Propietario sin nombre')

            with transaction.atomic():
                empresa, _ = Empresa.objects.get_or_create(
                    rut=rut_empresa,
                    defaults={'razon_social': razon_social}
                )

                # Strategy: If top-level rut_propietario exists, use it for all (Cert70 style).
                # If not, expect it in each calificacion (DJ1948 style).
                
                global_propietario = None
                if rut_propietario:
                    global_propietario, _ = Propietario.objects.get_or_create(
                        rut=rut_propietario,
                        empresa=empresa,
                        defaults={'nombre': nombre_propietario}
                    )

                for cal in calificaciones:
                    # Determine owner for this row
                    row_rut = cal.get('rut_propietario')
                    
                    current_propietario = global_propietario
                    if not current_propietario:
                        if not row_rut:
                            results["errors"].append(f"Falta RUT de propietario en fila (Fecha: {cal.get('fecha')})")
                            continue
                            
                        # Find or Create Owner for this row
                        # Name might be missing in row, use default or provided one
                        row_nombre = cal.get('nombre_propietario') or cal.get('nombre') or 'Propietario Sin Nombre'
                        current_propietario, created_prop = Propietario.objects.get_or_create(
                            rut=row_rut,
                            empresa=empresa,
                            defaults={'nombre': row_nombre}
                        )
                        # Optional: Update name if it was "Sin Nombre" before and we have a better one now
                        if not created_prop and current_propietario.nombre == 'Propietario Sin Nombre' and row_nombre != 'Propietario Sin Nombre':
                             current_propietario.nombre = row_nombre
                             current_propietario.save()


                    
                    # Prevent duplicates using update_or_create
                    # Lookup fields: Company, Owner, Date, Type, Amount (assuming these define uniqueness for a line)
                    CalificacionTributaria.objects.update_or_create(
                        empresa=empresa,
                        propietario=current_propietario,
                        fecha=pd.to_datetime(cal['fecha'], dayfirst=True).date(),
                        tipo=cal['tipo'],
                        monto_original=int(cal['monto']),
                        defaults={
                            'imputacion': cal.get('imputacion', 'SIN CLASIFICAR'),
                            'estado': 'pendiente'
                        }
                    )
                    results["created"] += 1
                    
        except Exception as e:
             results["errors"].append(str(e))

        return Response(results)
