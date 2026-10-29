from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class PermisoCreate(BaseModel):
    nombre: str = Field(
        min_length=3,
        max_length=150,
        pattern=r"^[A-Za-z][A-Za-z0-9_]*$",
    )

    descripcion: str | None = None


class PermisoUpdate(BaseModel):
    descripcion: str | None = None


class PermisoResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_permiso: int
    nombre: str
    descripcion: str | None