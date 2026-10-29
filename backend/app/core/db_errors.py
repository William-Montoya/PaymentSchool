from sqlalchemy.exc import DBAPIError


def get_postgres_error_message(
    exc: DBAPIError,
    fallback: str,
) -> str:
    original = getattr(exc, "orig", None)
    diag = getattr(original, "diag", None)

    message = getattr(diag, "message_primary", None)

    if message:
        return message

    return fallback