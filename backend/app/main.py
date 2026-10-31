from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.database import engine
from app.api.routers.estudiantes import router as estudiantes_router
from app.api.routers.catalogo_academico import router as catalogo_academico_router
from app.api.routers.inscripciones import router as inscripciones_router
from app.api.routers.precios import router as precios_router
from app.api.routers.obligaciones import router as obligaciones_router
from app.api.routers.pagos import router as pagos_router
from app.api.routers.saldos_favor import router as saldos_favor_router
from app.api.routers.becas import router as becas_router
from app.api.routers.descuentos import router as descuentos_router
from app.api.routers.evaluaciones import router as evaluaciones_router
from app.api.routers.solvencias import router as solvencias_router
from app.api.routers.reportes import router as reportes_router
from app.api.routers.tipos_documento import router as tipos_documento_router
from app.api.routers.expedientes import router as expedientes_router
from app.api.routers.contactos import router as contactos_router
from app.api.routers.documentos_expediente import router as documentos_expediente_router
from app.api.routers.cambios_carrera import router as cambios_carrera_router
from app.api.routers.movimientos_saldo import router as movimientos_saldo_router
from app.api.routers.notificaciones import router as notificaciones_router
from app.api.routers.empleados import router as empleados_router
from app.api.routers.permisos import router as permisos_router
from app.api.routers.roles import router as roles_router
from app.api.routers.usuarios import router as usuarios_router
from app.api.routers.auth import router as auth_router
from app.api.routers.auditorias import router as auditorias_router
from app.core.config import settings

app = FastAPI(
    title="Sistema de Control de Pagos",
    description="API para la gestión académica y financiera del colegio",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Sistema de Control de Pagos API",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected",
        }

    except Exception:
        return {
            "status": "error",
            "database": "disconnected",
        }

app.include_router(
    estudiantes_router,
    prefix="/api",
)

app.include_router(
    catalogo_academico_router,
    prefix="/api",
)

app.include_router(
    inscripciones_router,
    prefix="/api",
)

app.include_router(
    precios_router,
    prefix="/api",
)

app.include_router(
    obligaciones_router,
    prefix="/api",
)

app.include_router(
    pagos_router,
    prefix="/api",
)

app.include_router(
    saldos_favor_router,
    prefix="/api",
)

app.include_router(
    becas_router,
    prefix="/api",
)

app.include_router(
    descuentos_router,
    prefix="/api",
)
app.include_router(
    evaluaciones_router,
    prefix="/api",
)

app.include_router(
    solvencias_router,
    prefix="/api",
)

app.include_router(
    reportes_router,
    prefix="/api",
)

app.include_router(
    tipos_documento_router,
    prefix="/api",
)

app.include_router(
    expedientes_router,
    prefix="/api",
)

app.include_router(
    contactos_router,
    prefix="/api",
)

app.include_router(
    documentos_expediente_router,
    prefix="/api",
)

app.include_router(
    cambios_carrera_router,
    prefix="/api",
)

app.include_router(
    movimientos_saldo_router,
    prefix="/api",
)

app.include_router(
    notificaciones_router,
    prefix="/api",
)

app.include_router(
    empleados_router,
    prefix="/api",
)

app.include_router(
    permisos_router,
    prefix="/api",
)

app.include_router(
    roles_router,
    prefix="/api",
)

app.include_router(
    usuarios_router,
    prefix="/api",
)

app.include_router(
    auth_router,
    prefix="/api",
)

app.include_router(
    auditorias_router,
    prefix="/api",
)