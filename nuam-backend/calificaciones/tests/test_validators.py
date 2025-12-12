from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError
from calificaciones.validators import validate_rut, validate_positive

class ValidatorTests(SimpleTestCase):
    def test_validate_rut_valid(self):
        self.assertEqual(validate_rut("12.345.678-5"), "12.345.678-5")
        self.assertEqual(validate_rut("12345678-5"), "12345678-5")
        self.assertEqual(validate_rut("30.686.957-4"), "30.686.957-4")
        self.assertEqual(validate_rut("30686957-4"), "30686957-4")

    def test_validate_rut_invalid_dv(self):
        with self.assertRaises(ValidationError) as cm:
            validate_rut("12.345.678-K") # Should be 5
        self.assertIn("dígito verificador incorrecto", str(cm.exception))

    def test_validate_rut_invalid_format(self):
        with self.assertRaises(ValidationError) as cm:
            validate_rut("12.345.ABC-5")
        self.assertIn("cuerpo del RUT debe ser numérico", str(cm.exception))

    def test_validate_rut_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            validate_rut("1")
        self.assertIn("demasiado corto", str(cm.exception))

    def test_validate_positive_valid(self):
        self.assertEqual(validate_positive(100), 100)
        self.assertEqual(validate_positive(0), 0)

    def test_validate_positive_invalid(self):
        with self.assertRaises(ValidationError) as cm:
            validate_positive(-1)
        self.assertIn("El valor debe ser positivo", str(cm.exception))
