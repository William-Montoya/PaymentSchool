from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactoCreate(BaseModel):
    id_estudiante: int

    nombre: str = Field(
        min_length=1,
        max_length=150,
    )

    parentesco: str | None = Field(
        default=None,
        max_length=100,
    )

    telefono: str | None = Field(
        default=None,
        max_length=30,
    )

    whatsapp: str | None = Field(
        default=None,
        max_length=30,
    )

    email: EmailStr | None = None

    es_principal: bool = False


class ContactoUpdate(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    parentesco: str | None = Field(
        default=None,
        max_length=100,
    )

    telefono: str | None = Field(
        default=None,
        max_length=30,
    )

    whatsapp: str | None = Field(
        default=None,
        max_length=30,
    )

    email: EmailStr | None = None

    es_principal: bool | None = None


class ContactoEstadoUpdate(BaseModel):
    activo: bool


class ContactoResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_contacto: int
    id_estudiante: int

    nombre: str
    parentesco: str | None

    telefono: str | None
    whatsapp: str | None
    email: str | None

    es_principal: bool
    activo: bool