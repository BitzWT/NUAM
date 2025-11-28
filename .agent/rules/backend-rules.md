---
trigger: always_on
globs: nuam-backend/*
---

#CONTEXTO PARA BACKEND
- Siempre responde con código limpio, funcional y directamente aplicable.
- Usa Django 4+, Django REST Framework, PostgreSQL y Celery según corresponda.
- Para el frontend usa React con Vite, React Router y Axios.
- Respeta estrictamente el contexto del proyecto que está cargado en Knowledge.
- No inventes endpoints, modelos o estructuras que no estén en el contexto.
- Mantén coherencia entre backend y frontend.
- Cuando entregues código, incluye:
    - Rutas
    - Ubicación exacta del archivo
    - Código completo listo para pegar
- Sé directo y evita texto innecesario.
- Prioriza buenas prácticas, nombres claros y mantenibles.
- Aplica roles (admin, analista, auditor) en todo el código con permisos correctos.
- Mantén seguridad: JWT, cookies HttpOnly, CORS correcto.