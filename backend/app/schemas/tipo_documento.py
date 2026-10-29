from pydantic import BaseModel, ConfigDict, Field


class TipoDocumentoCreate(BaseModel):
    nombre: str = Field(
        min_length=1,
        max_length=150,
    )
    descripcion: str | None = None
    obligatorio: bool = False


class TipoDocumentoUpdate(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    descripcion: str | None = None
    obligatorio: bool | None = None


class TipoDocumentoEstadoUpdate(BaseModel):
    activo: bool


class TipoDocumentoResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_tipo_documento: int
    nombre: str
    descripcion: str | None
    obligatorio: bool
    activo: bool