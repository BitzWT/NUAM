from django.db.models import Sum
from calificaciones.models import CalificacionTributaria, CreditoIDPC

class Cert70Calculator:
    def __init__(self, empresa, propietario, anio):
        self.empresa = empresa
        self.propietario = propietario
        self.anio = anio

    def calculate(self):
        # Fetch qualifications for the year
        calificaciones = CalificacionTributaria.objects.filter(
            empresa=self.empresa,
            propietario=self.propietario,
            fecha__year=self.anio,
            estado='vigente'
        ).prefetch_related('creditos')

        detalles = []
        totales = {
            "monto_historico": 0,
            "monto_actualizado": 0,
            "rai": 0,
            "ddan": 0,
            "rex": 0,
            "inr": 0,
            "sac": 0,
            "credito_con_dev": 0,
            "credito_sin_dev": 0,
            "credito_restitucion": 0,
            "isfut": 0,
            "otros_creditos": 0
        }

        for cal in calificaciones:
            row = {
                "fecha": cal.fecha.strftime("%d-%m-%Y"),
                "tipo": cal.tipo,
                "monto_historico": cal.monto_original,
                "monto_actualizado": cal.monto_reajustado or cal.monto_original,
                "imputacion": cal.imputacion or "",
                "rai": 0,
                "ddan": 0,
                "rex": 0,
                "inr": 0,
                "sac": 0,
                "credito_con_dev": 0,
                "credito_sin_dev": 0,
                "credito_restitucion": 0,
                "isfut": 0,
                "otros_creditos": 0
            }

            # Map imputacion to columns
            monto = row["monto_actualizado"]
            imp = (cal.imputacion or "").upper()
            
            if "RAI" in imp:
                row["rai"] = monto
            elif "DDAN" in imp:
                row["ddan"] = monto
            elif "REX" in imp:
                row["rex"] = monto
            elif "INR" in imp:
                row["inr"] = monto
            elif "SAC" in imp:
                row["sac"] = monto
            
            # Process credits
            for cred in cal.creditos.all():
                c_tipo = (cred.tipo or "").lower()
                c_monto = cred.monto
                
                if "con devolución" in c_tipo or "con devolucion" in c_tipo:
                    row["credito_con_dev"] += c_monto
                elif "sin devolución" in c_tipo or "sin devolucion" in c_tipo:
                    row["credito_sin_dev"] += c_monto
                elif "restitución" in c_tipo or "restitucion" in c_tipo:
                    row["credito_restitucion"] += c_monto
                elif "isfut" in c_tipo:
                    row["isfut"] += c_monto
                else:
                    row["otros_creditos"] += c_monto

            # Accumulate totals
            totales["monto_historico"] += row["monto_historico"]
            totales["monto_actualizado"] += row["monto_actualizado"]
            totales["rai"] += row["rai"]
            totales["ddan"] += row["ddan"]
            totales["rex"] += row["rex"]
            totales["inr"] += row["inr"]
            totales["sac"] += row["sac"]
            totales["credito_con_dev"] += row["credito_con_dev"]
            totales["credito_sin_dev"] += row["credito_sin_dev"]
            totales["credito_restitucion"] += row["credito_restitucion"]
            totales["isfut"] += row["isfut"]
            totales["otros_creditos"] += row["otros_creditos"]

            detalles.append(row)

        return totales, detalles
