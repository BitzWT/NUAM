import pdfplumber
import re
from datetime import datetime

class PDFParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_text(self):
        """Extracts text from the PDF file."""
        text = ""
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text

    def parse_data(self):
        """Parses the extracted text to find relevant data."""
        text = self.extract_text()
        
        # Determine strict parsing strategy based on content
        if "1948" in text or "Retiros" in text:
            return self._parse_dj1948(text)
        
        # Legacy/Generic Parsing
        data = {
            "rut_empresa": self._extract_rut(text, "empresa"),
            "rut_propietario": self._extract_rut(text, "propietario"),
            "fecha": self._extract_date(text),
            "calificaciones": self._extract_calificaciones(text)
        }
        return data

    def _parse_dj1948(self, text):
        """Specialized parser for DJ1948 Structure."""
        data = {
            "rut_empresa": self._extract_rut(text, "empresa"),
            "rut_propietario": None, # Will be extracted per row
            "fecha": self._extract_date(text),
            "calificaciones": []
        }

        # Use pdfplumber table extraction for better accuracy
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        # Clean row data (remove None and empty strings)
                        cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                        
                        # Heuristic: Check if row looks like a data row (Pattern: RUT, Name, Code, Amount)
                        # 1. RUT Search: Scan ALL columns, not just first 2
                        rut_candidate = next((cell for cell in cleaned_row if self._is_valid_rut(cell)), None)
                        
                        if rut_candidate:
                            # 2. Type/Code Mapping
                            tipo_mapping = {
                                "DIV": "dividendo",
                                "RET": "retiro",
                                "REM": "remesa",
                                "RAI": "retiro", # Default fallback
                                "REX": "retiro"
                            }
                            found_code = None
                            found_tipo = "retiro" # Default
                            found_imputacion = "SIN CLASIFICAR"
                            for cell in cleaned_row:
                                upper_cell = cell.upper()
                                # Handle cases where code might be joined with other text or strictly exact
                                # For safety, look for exact match in split words or the cell itself
                                if upper_cell in tipo_mapping or any(word in tipo_mapping for word in upper_cell.split()):
                                    # Identify which code it is
                                    code = upper_cell if upper_cell in tipo_mapping else next((w for w in upper_cell.split() if w in tipo_mapping), "RAI")
                                    found_code = code
                                    found_tipo = tipo_mapping.get(code, "retiro")
                                    found_imputacion = code
                                    break
                            
                            # 3. Amount Extraction: Valid numbers, pick largest (heuristic for 'Monto Actualizado')
                            found_monto = 0
                            numeric_values = []
                            for cell in cleaned_row:
                                # Remove common currency formatting (dots, commas, symbols)
                                clean_val = cell.replace("$", "").replace(".", "").replace(",", "").replace(" ", "").strip()
                                # Ensure it's a number and not a date part (simple check)
                                if clean_val.isdigit():
                                    val = int(clean_val)
                                    # Heuristic: Amounts in DJ1948 are usually significant. 
                                    # Ignore unlikely small integers that could be flags/counts unless they are the ONLY number.
                                    # Also ignore if it matches the RUT digits (unlikely but possible cleanup artifact).
                                    numeric_values.append(val)
                            
                            if numeric_values:
                                found_monto = max(numeric_values)

                            # 4. Date Extraction
                            row_date = data["fecha"] # Fallback to document date
                            date_in_row = next((cell for cell in cleaned_row if re.match(r"\d{1,2}[-/]\d{1,2}[-/]\d{4}", cell)), None)
                            if date_in_row:
                                row_date = date_in_row

                            # 5. Name Extraction (Heuristic)
                            # The name is usually a string (not a date, not a number, not the RUT).
                            # We pick the longest remaining string that DOESN'T look like a transaction type.
                            found_nombre = None
                            potential_names = []
                            KEYWORDS_TO_IGNORE = ["RETIRO", "REMESA", "DIVIDENDO", "DEVOLUCION", "CAPITAL", "RAI", "DDAN", "REX", "RAP", "SAC", "ISFUT"]
                            
                            for cell in cleaned_row:
                                # Clean potential name
                                clean_cell = cell.strip()
                                print(f"DEBUG CELL: '{clean_cell}'")
                                
                                # Skip if it looks like the RUT we just found or another RUT
                                if self._is_valid_rut(clean_cell) or clean_cell == rut_candidate:
                                    print("  -> Skipped (RUT)")
                                    continue
                                
                                # Skip if it's a date
                                if re.match(r"\d{1,2}[-/]\d{1,2}[-/]\d{4}", clean_cell):
                                    print("  -> Skipped (Date)")
                                    continue
                                
                                # Skip if it's purely numeric/currency
                                if re.match(r"^[\d\.,\$]+$", clean_cell.replace(" ", "")):
                                    print("  -> Skipped (Numeric)")
                                    continue
                                    
                                # Skip if it contains known transaction keywords (e.g. "RETIRO / RAI")
                                if any(kw in clean_cell.upper() for kw in KEYWORDS_TO_IGNORE):
                                    print("  -> Skipped (Keyword)")
                                    continue
                                    
                                # Ideally names have letters.
                                if re.search(r"[a-zA-Z]", clean_cell):
                                    print("  -> Candidate!")
                                    potential_names.append(clean_cell)

                            if potential_names:
                                # Pick the longest string as the name
                                found_nombre = max(potential_names, key=len)
                                print(f"DEBUG SELECTED: {found_nombre}")
                                
                            data["calificaciones"].append({
                                "fecha": row_date,
                                "rut_propietario": rut_candidate,
                                "nombre_propietario": found_nombre,
                                "tipo": found_tipo,
                                "monto": found_monto,
                                "imputacion": found_imputacion,
                                "original_line": " | ".join(cleaned_row)
                            })
                            
        return data

    def _is_valid_rut(self, text):
        return bool(re.search(r"\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b", text))

    def _extract_rut(self, text, entity_type):
        """
        Extracts RUT based on entity type.
        """
        # Regex for Chilean RUT: 12.345.678-9 or 12345678-9
        rut_pattern = r"\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b"
        ruts = re.findall(rut_pattern, text)
        
        if not ruts:
            return None

        # Improved Heuristic:
        # Empresa RUT is usually at the TOP (Header or Box A)
        # We assume the first RUT in the text (if not inside a table context) is the Declarante
        return ruts[0]

    def _extract_date(self, text):
        """Extracts the document date."""
        # Pattern DD/MM/YYYY or DD-MM-YYYY
        date_pattern = r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b"
        dates = re.findall(date_pattern, text)
        if dates:
            return dates[0]
        return datetime.now().strftime("%Y-%m-%d")

    def _extract_calificaciones(self, text):
        """
        Legacy generic extraction (kept for fallback)
        """
        calificaciones = []
        lines = text.split('\n')
        for line in lines:
            if re.search(r"\d{1,2}[-/]\d{1,2}[-/]\d{4}", line) and re.search(r"\d", line):
                line_lower = line.lower()
                tipo = None
                if "retiro" in line_lower:
                    tipo = "retiro"
                elif "remesa" in line_lower:
                    tipo = "remesa"
                elif "dividendo" in line_lower:
                    tipo = "dividendo"
                
                if not tipo:
                    continue

                imputacion = "RAI" # Default
                
                numbers = re.findall(r"[\d\.]+", line)
                if numbers:
                    try:
                        monto_str = numbers[-1].replace(".", "")
                        monto = int(monto_str)
                        calificaciones.append({
                            "fecha": re.findall(r"\d{1,2}[-/]\d{1,2}[-/]\d{4}", line)[0],
                            "tipo": tipo,
                            "monto": monto,
                            "imputacion": imputacion,
                            "original_line": line
                        })
                    except ValueError:
                        continue
        return calificaciones
