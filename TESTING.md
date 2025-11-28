# Guía de Pruebas (Testing)

Este documento explica cómo ejecutar las pruebas unitarias y de API para el proyecto NUAM.

## 1. Pruebas de Backend (Pytest)

Estas pruebas verifican la lógica interna de Django, incluyendo modelos, autenticación y vistas.

### Requisitos
Asegúrate de tener instaladas las dependencias de prueba (ya incluidas si ejecutaste `pip install pytest pytest-django`):
```bash
pip install pytest pytest-django
```

### Ejecutar Pruebas
Desde la carpeta `nuam-backend`, ejecuta:

```bash
pytest
```

Esto buscará y ejecutará automáticamente todos los archivos de prueba en la carpeta `tests/`.

**Opciones útiles:**
- `pytest -v`: Muestra más detalles (verbose).
- `pytest tests/test_auth.py`: Ejecuta solo un archivo específico.
- `pytest -k "login"`: Ejecuta solo los tests que contengan "login" en su nombre.

---

## 2. Pruebas de API (Postman)

Hemos generado una colección de Postman para probar los endpoints HTTP externamente.

### Importar Colección
1. Abre **Postman**.
2. Haz clic en **Import** (arriba a la izquierda).
3. Arrastra o selecciona el archivo `nuam_postman_collection.json` ubicado en la raíz del proyecto.

### Usar la Colección
La colección está configurada para gestionar la autenticación automáticamente.

1. **Login**:
   - Abre la carpeta **Auth** > **Login**.
   - En el **Body**, asegúrate de que las credenciales sean correctas (por defecto `admin_test` / `password123`).
   - Haz clic en **Send**.
   - **Magia**: Un script automático guardará el `access_token` y `refresh_token` en las variables de entorno de Postman.

2. **Otras Peticiones (ej. Users, Empresas)**:
   - Simplemente abre cualquier otra petición (ej. **Users** > **List Users**).
   - Haz clic en **Send**.
   - El token se inyectará automáticamente en el header `Authorization`.

### Solución de Problemas
- **401 Unauthorized**: Probablemente tu token expiró. Vuelve a ejecutar el request de **Login** para renovarlo.
- **Connection Refused**: Asegúrate de que el servidor backend esté corriendo (`python manage.py runserver`).

---

## 3. Pruebas de Seguridad

### Análisis Estático (Bandit)
Escanea el código en busca de vulnerabilidades conocidas.
```bash
bandit -r . -x ./tests
```

### Tests de Ataque (XSS/SQLi)
Ejecuta simulaciones de ataques para verificar la robustez de la API.
```bash
pytest tests/test_security.py
```
