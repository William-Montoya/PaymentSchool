from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.db_errors import (
    get_postgres_error_message,
)
from app.repositories.saldo_favor_repository import (
    SaldoFavorRepository,
)
from app.schemas.pago import (
    AplicarSaldoFavorCreate,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class SaldoFavorService:

    @staticmethod
    def obtener(
        db: Session,
        id_saldo_favor: int,
    ) -> dict:

        saldo = SaldoFavorRepository.get_by_id(
            db,
            id_saldo_favor,
        )

        if saldo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saldo a favor no encontrado",
            )

        return saldo

    @staticmethod
    def listar(
        db: Session,
        id_estudiante: int | None = None,
        estado: str | None = None,
    ):
        return SaldoFavorRepository.list(
            db=db,
            id_estudiante=id_estudiante,
            estado=estado,
        )

    @staticmethod
    def aplicar(
        db: Session,
        id_saldo_favor: int,
        data: AplicarSaldoFavorCreate,
        id_usuario: int,
    ) -> dict:

        saldo_anterior = SaldoFavorService.obtener(
            db,
            id_saldo_favor,
        )

        if saldo_anterior["estado"] != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El saldo a favor no está activo",
            )

        try:
            SaldoFavorRepository.aplicar(
                db=db,
                id_saldo_favor=id_saldo_favor,
                id_obligacion=data.id_obligacion,
                monto=data.monto,
            )

            saldo_actualizado = (
                SaldoFavorService.obtener(
                    db,
                    id_saldo_favor,
                )
            )

            resultado = {
                "mensaje": (
                    "Saldo a favor aplicado correctamente"
                ),
                "id_saldo_favor":
                    id_saldo_favor,
                "id_obligacion":
                    data.id_obligacion,
                "monto_aplicado":
                    data.monto,
                "monto_disponible": (
                    saldo_actualizado[
                        "monto_disponible"
                    ]
                ),
                "estado":
                    saldo_actualizado["estado"],
            }

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="APLICAR_SALDO_FAVOR",
                tabla_afectada="saldo_favor",
                id_registro=id_saldo_favor,
                descripcion=(
                    "Aplicación de saldo a favor "
                    f"a la obligación "
                    f"{data.id_obligacion}"
                ),
                datos_anteriores=
                    saldo_anterior,
                datos_nuevos={
                    "saldo_favor":
                        saldo_actualizado,
                    "id_obligacion":
                        data.id_obligacion,
                    "monto_aplicado":
                        data.monto,
                },
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    (
                        "No fue posible aplicar "
                        "el saldo a favor"
                    ),
                ),
            )

        except Exception:
            db.rollback()
            raise

        return resultado