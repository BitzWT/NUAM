from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock
from calificaciones.services.pdf_parser import PDFParser

class PDFParserTests(SimpleTestCase):
    def setUp(self):
        self.sample_text = """
        CERTIFICADO N° 123
        Fecha: 15/04/2023
        
        Empresa:
        RUT: 76.543.210-K
        Razon Social: EMPRESA DE EJEMPLO SPA
        
        Propietario:
        RUT: 12.345.678-9
        Nombre: JUAN PEREZ
        
        Detalle de Retiros:
        Fecha       Tipo        Monto
        01/01/2023  Retiro      1.000.000
        15/03/2023  Remesa      500.000
        """

    @patch('pdfplumber.open')
    def test_extract_text(self, mock_open):
        # Mock the PDF object and page
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample Text"
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_open.return_value = mock_pdf

        parser = PDFParser("dummy.pdf")
        text = parser.extract_text()
        
        self.assertEqual(text, "Sample Text\n")

    @patch('calificaciones.services.pdf_parser.PDFParser.extract_text')
    def test_parse_data(self, mock_extract_text):
        mock_extract_text.return_value = self.sample_text
        
        parser = PDFParser("dummy.pdf")
        data = parser.parse_data()
        
        self.assertEqual(data['rut_empresa'], '76.543.210-K')
        self.assertEqual(data['rut_propietario'], '12.345.678-9')
        self.assertEqual(data['fecha'], '15/04/2023')
        
        self.assertEqual(len(data['calificaciones']), 2)
        
        # Check first qualification
        self.assertEqual(data['calificaciones'][0]['fecha'], '01/01/2023')
        self.assertEqual(data['calificaciones'][0]['tipo'], 'retiro')
        self.assertEqual(data['calificaciones'][0]['monto'], 1000000)
        
        # Check second qualification
        self.assertEqual(data['calificaciones'][1]['fecha'], '15/03/2023')
        self.assertEqual(data['calificaciones'][1]['tipo'], 'remesa')
        self.assertEqual(data['calificaciones'][1]['monto'], 500000)
