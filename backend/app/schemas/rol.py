from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.schemas.permiso import (
    PermisoResponse,
)


class RolCreate(BaseModel):
    nombre: str = Field(
        min_length=2,
        max_length=100,
        pattern=r"^[A-Za-z][A-Za-z0-9_]*$",
    )

    descripcion: str | None = None


class RolUpdate(BaseModel):
    descripcion: str | None = None


class RolEstadoUpdate(BaseModel):
    activo: bool


class RolPermisosUpdate(BaseModel):
    ids_permiso: list[int] = Field(
        default_factory=list
    )


class RolResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_rol: int
    nombre: str
    descripcion: str | None
    activo: bool


class RolDetalleResponse(RolResponse):
    permisos: list[PermisoResponse]