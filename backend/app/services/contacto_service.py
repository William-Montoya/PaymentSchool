from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.contacto import Contacto
from app.repositories.contacto_repository import (
    ContactoRepository,
)
from app.repositories.estudiante_repository import (
    EstudianteRepository,
)
from app.schemas.contacto import (
    ContactoCreate,
    ContactoEstadoUpdate,
    ContactoUpdate,
)


class ContactoService:

    @staticmethod
    def obtener(
        db: Session,
        id_contacto: int,
    ) -> Contacto:

        contacto = ContactoRepository.get_by_id(
            db,
            id_contacto,
        )

        if contacto is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contacto no encontrado",
            )

        return contacto

    @staticmethod
    def crear(
        db: Session,
        data: ContactoCreate,
    ) -> Contacto:

        estudiante = (
            EstudianteRepository
            .get_by_id(
                db,
                data.id_estudiante,
            )
        )

        if estudiante is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )

        contacto = Contacto(
            **data.model_dump()
        )

        if data.es_principal:
            ContactoRepository.quitar_principal(
                db,
                data.id_estudiante,
            )

        db.add(contacto)
        db.commit()
        db.refresh(contacto)

        return contacto

    @staticmethod
    def actualizar(
        db: Session,
        id_contacto: int,
        data: ContactoUpdate,
    ) -> Contacto:

        contacto = ContactoService.obtener(
            db,
            id_contacto,
        )

        cambios = data.model_dump(
            exclude_unset=True
        )

        if cambios.get("es_principal") is True:
            ContactoRepository.quitar_principal(
                db=db,
                id_estudiante=
                    contacto.id_estudiante,
                excluir_id=id_contacto,
            )

        for campo, valor in cambios.items():
            setattr(
                contacto,
                campo,
                valor,
            )

        db.commit()
        db.refresh(contacto)

        return contacto

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_contacto: int,
        data: ContactoEstadoUpdate,
    ) -> Contacto:

        contacto = ContactoService.obtener(
            db,
            id_contacto,
        )

        contacto.activo = data.activo

        if not data.activo:
            contacto.es_principal = False

        db.commit()
        db.refresh(contacto)

        return contacto