from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class AuthRepository:

    @staticmethod
    def get_by_username(
        db: Session,
        username: str,
    ) -> Usuario | None:

        stmt = (
            select(Usuario)
            .where(
                func.lower(
                    Usuario.username
                )
                == username.lower()
            )
        )

        return db.scalar(stmt)

    @staticmethod
    def actualizar_ultimo_acceso(
        db: Session,
        usuario: Usuario,
    ) -> None:

        usuario.ultimo_acceso = (
            func.current_timestamp()
        )

        db.flush()