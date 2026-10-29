from app.core.config import settings
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

STORAGE_ROOT = Path(
    settings.paymentschool_storage_dir
).resolve()


@dataclass(frozen=True)
class StoredFile:
    original_name: str
    relative_path: str
    absolute_path: Path
    media_type: str
    size: int


ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


def _validar_firma(
    extension: str,
    header: bytes,
) -> bool:

    if extension == ".pdf":
        return header.startswith(b"%PDF-")

    if extension == ".png":
        return header.startswith(
            b"\x89PNG\r\n\x1a\n"
        )

    if extension in {".jpg", ".jpeg"}:
        return header.startswith(
            b"\xff\xd8\xff"
        )

    return False


def validar_archivo(
    archivo: UploadFile,
) -> tuple[str, str, str]:

    if not archivo.filename:
        raise ValueError(
            "El archivo no tiene nombre"
        )

    # Elimina cualquier ruta enviada por el cliente.
    nombre_original = Path(
        archivo.filename
    ).name

    extension = Path(
        nombre_original
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Solo se permiten archivos PDF, JPG, JPEG o PNG"
        )

    header = archivo.file.read(16)
    archivo.file.seek(0)

    if not _validar_firma(
        extension,
        header,
    ):
        raise ValueError(
            "El contenido del archivo no coincide "
            "con un formato permitido"
        )

    media_type = ALLOWED_EXTENSIONS[
        extension
    ]

    return (
        nombre_original,
        extension,
        media_type,
    )


def guardar_archivo_expediente(
    archivo: UploadFile,
    id_expediente: int,
) -> StoredFile:

    (
        nombre_original,
        extension,
        media_type,
    ) = validar_archivo(
        archivo
    )

    nombre_interno = (
        f"{uuid4().hex}{extension}"
    )

    relative_path = (
        Path("expedientes")
        / str(id_expediente)
        / nombre_interno
    )

    absolute_path = (
        STORAGE_ROOT
        / relative_path
    ).resolve()

    absolute_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    total = 0

    try:
        with absolute_path.open("wb") as destino:

            while True:
                chunk = archivo.file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total += len(chunk)

                if total > MAX_FILE_SIZE:
                    raise ValueError(
                        "El archivo excede el límite "
                        "máximo de 10 MB"
                    )

                destino.write(chunk)

    except Exception:
        absolute_path.unlink(
            missing_ok=True
        )
        raise

    return StoredFile(
        original_name=nombre_original,
        relative_path=relative_path.as_posix(),
        absolute_path=absolute_path,
        media_type=media_type,
        size=total,
    )


def resolver_ruta_archivo(
    relative_path: str,
) -> Path:

    path = (
        STORAGE_ROOT
        / relative_path
    ).resolve()

    # Evita path traversal.
    if (
        path != STORAGE_ROOT
        and STORAGE_ROOT
        not in path.parents
    ):
        raise ValueError(
            "Ruta de almacenamiento inválida"
        )

    return path


def eliminar_archivo(
    relative_path: str | None,
) -> None:

    if not relative_path:
        return

    try:
        path = resolver_ruta_archivo(
            relative_path
        )

        path.unlink(
            missing_ok=True
        )

    except ValueError:
        # Nunca intentamos borrar algo fuera
        # de STORAGE_ROOT.
        return


def obtener_media_type(
    filename: str,
) -> str:

    extension = Path(
        filename
    ).suffix.lower()

    return ALLOWED_EXTENSIONS.get(
        extension,
        "application/octet-stream",
    )