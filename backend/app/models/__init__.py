from app.models.ciclo_escolar import CicloEscolar
from app.models.carrera import Carrera
from app.models.carrera_ciclo import CarreraCiclo
from app.models.grado import Grado
from app.models.estudiante import Estudiante
from app.models.inscripcion import Inscripcion
from app.models.tipo_documento import TipoDocumento
from app.models.expediente import Expediente
from app.models.documento_expediente import DocumentoExpediente
from app.models.contacto import Contacto
from app.models.obligacion import Obligacion
from app.models.pago import Pago
from app.models.aplicacion_pago import AplicacionPago
from app.models.precio_carrera import PrecioCarrera
from app.models.beca import Beca
from app.models.beca_estudiante import BecaEstudiante
from app.models.descuento import Descuento
from app.models.descuento_obligacion import DescuentoObligacion
from app.models.cambio_carrera import CambioCarrera
from app.models.saldo_favor import SaldoFavor
from app.models.movimiento_saldo import MovimientoSaldo
from app.models.recibo import Recibo
from app.models.solvencia import Solvencia
from app.models.evaluacion import Evaluacion
from app.models.empleado import Empleado
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol
from app.models.permiso import Permiso
from app.models.rol_permiso import RolPermiso
from app.models.auditoria import Auditoria
from app.models.notificacion import Notificacion
from app.models.notificacion_destinatario import NotificacionDestinatario
from app.models.beca_obligacion import BecaObligacion


__all__ = [
    "CicloEscolar",
    "Carrera",
    "CarreraCiclo",
    "Grado",
    "Estudiante",
    "Inscripcion",
    "TipoDocumento",
    "Expediente",
    "DocumentoExpediente",
    "Contacto",
    "Obligacion",
    "Pago",
    "AplicacionPago",
    "PrecioCarrera",
    "Beca",
    "BecaEstudiante",
    "Descuento",
    "DescuentoObligacion",
    "CambioCarrera",
    "SaldoFavor",
    "MovimientoSaldo",
    "Recibo",
    "Solvencia",
    "Evaluacion",
    "Empleado",
    "Usuario",
    "Rol",
    "UsuarioRol",
    "Permiso",
    "RolPermiso",
    "Auditoria",
    "Notificacion",
    "BecaObligacion",
    "NotificacionDestinatario",
]