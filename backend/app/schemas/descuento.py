from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class DescuentoCreate(BaseModel):
    nombre: str = Field(
        min_length=1,
        max_length=150,
    )

    descripcion: str | None = None

    porcentaje: Decimal | None = Field(
        default=None,
        gt=0,
        le=100,
        max_digits=5,
        decimal_places=2,
    )

    monto_fijo: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    @model_validator(mode="after")
    def validar_tipo(self):
        if (
            self.porcentaje is None
            and self.monto_fijo is None
        ):
            raise ValueError(
                "Debe indicar porcentaje o monto fijo"
            )

        if (
            self.porcentaje is not None
            and self.monto_fijo is not None
        ):
            raise ValueError(
                "Indique porcentaje o monto fijo, no ambos"
            )

        return self


class DescuentoEstadoUpdate(BaseModel):
    activo: bool


class DescuentoResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_descuento: int
    nombre: str
    descripcion: str | None

    porcentaje: Decimal | None
    monto_fijo: Decimal | None

    activo: bool


class DescuentoAplicacionResponse(BaseModel):
    id_descuento_obligacion: int

    id_descuento: int
    descuento: str

    id_obligacion: int
    concepto: str

    monto_aplicado: Decimal
    fecha_aplicacion: datetime