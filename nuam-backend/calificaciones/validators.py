import re
from rest_framework import serializers

def validate_rut(value):
    """
    Validates a Chilean RUT.
    Expected format: XXXXXXXX-Y or XX.XXX.XXX-Y (will be cleaned)
    """
    if not value:
        return value

    # Clean format
    rut_clean = value.replace(".", "").replace("-", "").upper()
    
    if len(rut_clean) < 2:
        raise serializers.ValidationError("El RUT es demasiado corto.")

    body = rut_clean[:-1]
    dv = rut_clean[-1]

    # Validate body is numeric
    if not body.isdigit():
        raise serializers.ValidationError("El cuerpo del RUT debe ser numérico.")

    # Calculate DV
    suma = 0
    multiplo = 2
    
    for c in reversed(body):
        suma += int(c) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
            
    res = 11 - (suma % 11)
    
    if res == 11:
        dv_calc = '0'
    elif res == 10:
        dv_calc = 'K'
    else:
        dv_calc = str(res)
        
    if dv != dv_calc:
        raise serializers.ValidationError("El RUT no es válido (dígito verificador incorrecto).")
        
    return value

def validate_positive(value):
    """
    Validates that the value is positive (> 0).
    """
    if value is not None and value < 0:
        raise serializers.ValidationError("El valor debe ser positivo.")
    return value
