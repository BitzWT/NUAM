# PROYECTO NUAM – CONTEXTO COMPLETO

## Descripción general
NUAM es un sistema web compuesto por un backend Django REST Framework y un frontend React. Su propósito es gestionar y auditar calificaciones tributarias, con manejo de usuarios, roles, MFA, carga masiva, historial de cambios y exportaciones.

## Tecnologías
- **Backend**: Django 4+, Django REST Framework, MySQL, Celery + Redis (opcional), SimpleJWT, django-two-factor-auth (o custom OTP).
- **Frontend**: React + Vite, Axios, React Router, Tailwind (opcional).
- **Librerías clave**: reportlab/weasyprint (PDF), openpyxl (Excel).

## Roles del sistema
1. **admin**: Acceso total.
2. **analista**: CRUD de calificaciones + carga masiva.
3. **auditor**: Solo lectura + acceso historial.

## Backend – Modelos principales
1. **User** (AbstractUser): campo `role`.
2. **Calificacion**: instrumento, fecha, monto, factor, estado, created_by, timestamps.
3. **HistorialCalificacion**: FK calificacion, accion, usuario, antes (JSON), despues (JSON), timestamp.
4. **ArchivoSubido**: nombre, tipo, archivo, subido_por, creado.

## Backend – Funcionalidades
- Autenticación JWT + Cookies HttpOnly (opcional).
- MFA.
- CRUD Calificacion.
- Historial automático (signals).
- Carga masiva DJ1948 (validación filas).
- Exportación PDF/Excel.
- Health check `/api/health/`.

## Reglas de negocio
- Todo cambio genera historial.
- Auditores solo lectura.
- Analistas modifican (propias o todas).
- Carga masiva valida y reporta errores.
- Exportaciones respetan filtros.

## Frontend – Pantallas
1. Login
2. MFA
3. Dashboard
4. Gestión de calificaciones (Listar, Crear, Editar, Eliminar, Historial)
5. Carga masiva DJ1948
6. Exportación PDF/Excel

## Frontend – Reglas técnicas
- Axios con `withCredentials`.
- AuthContext.
- ProtectedRoute.
- Modularidad.

## Flujo del usuario
Login -> MFA -> Dashboard -> Listado -> CRUD -> Historial -> Carga masiva -> Exportaciones.
