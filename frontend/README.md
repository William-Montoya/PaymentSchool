# PaymentSchool frontend

## Configuración de producción

Configure `VITE_API_URL` en Vercel con la URL pública del backend, sin el
`/api` final:

```text
VITE_API_URL=https://paymentschool.onrender.com
```

El cliente agrega `/api` automáticamente. Por eso las solicitudes de
autenticación se envían a `/api/auth/login` y no a `/auth/login`.

En Render, configure `CORS_ORIGINS` con el origen exacto de Vercel, sin una
barra final. Puede indicar varios orígenes separados por comas:

```text
CORS_ORIGINS=https://payment-school-hrq3du7ig-william-4d5e.vercel.app
```

Después de cambiar `VITE_API_URL`, vuelva a desplegar el frontend, ya que Vite
incluye las variables durante la compilación.
