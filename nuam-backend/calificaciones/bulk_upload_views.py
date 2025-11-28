import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Empresa, Propietario, CalificacionTributaria

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
