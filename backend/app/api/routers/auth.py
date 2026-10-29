from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    CurrentUser,
)
from app.core.database import get_db
from app.schemas.auth import TokenResponse
from app.schemas.usuario import (
    UsuarioDetalleResponse,
)
from app.services.auth_service import (
    AuthService,
)
from app.services.usuario_service import (
    UsuarioService,
)

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data:
        OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return AuthService.login(
        db=db,
        username=form_data.username,
        password=form_data.password,
    )

@router.get(
    "/me",
    response_model=UsuarioDetalleResponse,
)
def me(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    return UsuarioService.obtener(
        db,
        current_user.id_usuario,
    )