#!/usr/bin/env python
"""
PaymentSchool - prueba E2E del backend.

IMPORTANTE:
- Ejecutar solamente contra paymentschool_test.
- Requiere que la API ya esté levantada.
- No guarda ni imprime la contraseña usada para el login.
- Crea datos únicos de prueba y desactiva el usuario limitado creado al final.
- No elimina datos históricos.

Variables requeridas:
    E2E_USERNAME
    E2E_PASSWORD
    E2E_CONFIRM_DB=paymentschool_test

Variable opcional:
    E2E_BASE_URL=http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4


BASE_URL = os.getenv(
    "E2E_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

USERNAME = os.getenv("E2E_USERNAME")
PASSWORD = os.getenv("E2E_PASSWORD")
CONFIRM_DB = os.getenv("E2E_CONFIRM_DB")

TIMEOUT = 20

HTTP_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
}


class E2EError(RuntimeError):
    pass


def require_env() -> None:
    if CONFIRM_DB != "paymentschool_test":
        raise E2EError(
            "Prueba detenida: define "
            "E2E_CONFIRM_DB=paymentschool_test."
        )

    if not USERNAME:
        raise E2EError(
            "Falta la variable E2E_USERNAME."
        )

    if not PASSWORD:
        raise E2EError(
            "Falta la variable E2E_PASSWORD."
        )


def parse_body(raw: bytes) -> Any:
    if not raw:
        return None

    text = raw.decode(
        "utf-8",
        errors="replace",
    )

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def http(
    method: str,
    path: str,
    *,
    token: str | None = None,
    json_body: Any = None,
    form_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    expected: tuple[int, ...] = (200,),
) -> Any:
    method = method.upper()

    if method not in HTTP_METHODS:
        raise ValueError(
            f"Método HTTP no soportado: {method}"
        )

    url = f"{BASE_URL}{path}"

    if params:
        clean_params = {
            key: value
            for key, value in params.items()
            if value is not None
        }

        if clean_params:
            url = (
                f"{url}?"
                f"{urlencode(clean_params)}"
            )

    headers = {
        "Accept": "application/json",
    }

    if token:
        headers["Authorization"] = (
            f"Bearer {token}"
        )

    data: bytes | None = None

    if json_body is not None:
        data = json.dumps(
            json_body,
            ensure_ascii=False,
        ).encode("utf-8")

        headers["Content-Type"] = (
            "application/json"
        )

    elif form_body is not None:
        data = urlencode(
            form_body
        ).encode("utf-8")

        headers["Content-Type"] = (
            "application/x-www-form-urlencoded"
        )

    request = Request(
        url=url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(
            request,
            timeout=TIMEOUT,
        ) as response:
            status_code = response.status
            body = parse_body(
                response.read()
            )

    except HTTPError as exc:
        status_code = exc.code
        body = parse_body(
            exc.read()
        )

    except URLError as exc:
        raise E2EError(
            "No fue posible conectar con la API "
            f"en {BASE_URL}: {exc}"
        ) from exc

    if status_code not in expected:
        raise E2EError(
            f"{method} {path} devolvió "
            f"{status_code}; esperado {expected}. "
            f"Respuesta: {body!r}"
        )

    return body


def as_decimal(
    value: Any,
) -> Decimal:
    return Decimal(str(value))


def assert_equal(
    actual: Any,
    expected: Any,
    message: str,
) -> None:
    if actual != expected:
        raise E2EError(
            f"{message}. "
            f"Esperado={expected!r}, "
            f"actual={actual!r}"
        )


def assert_true(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise E2EError(message)


def permission_names(
    me: dict[str, Any],
) -> set[str]:
    return {
        item["nombre"]
        for item in me.get(
            "permisos",
            [],
        )
    }


def find_permission_id(
    permisos: list[dict[str, Any]],
    nombre: str,
) -> int:
    for permiso in permisos:
        if permiso.get("nombre") == nombre:
            return int(
                permiso["id_permiso"]
            )

    raise E2EError(
        f"No existe el permiso {nombre}."
    )


def audit_event(
    token: str,
    *,
    accion: str,
    id_registro: int,
    actor_id: int,
) -> dict[str, Any]:
    rows = http(
        "GET",
        "/api/auditoria",
        token=token,
        params={
            "accion": accion,
            "id_registro": id_registro,
            "limit": 50,
        },
    )

    for row in rows:
        if (
            row.get("accion") == accion
            and row.get("id_registro")
            == id_registro
        ):
            assert_equal(
                row.get("id_usuario"),
                actor_id,
                (
                    f"El evento {accion} no "
                    "quedó asociado al actor "
                    "autenticado"
                ),
            )
            return row

    raise E2EError(
        "No se encontró auditoría para "
        f"{accion} / {id_registro}."
    )


def main() -> int:
    require_env()

    suffix = (
        datetime.now()
        .strftime("%Y%m%d%H%M%S")
        + "_"
        + uuid4().hex[:6]
    )

    today = date.today()
    year = today.year

    start_date = date(
        year,
        1,
        1,
    ).isoformat()

    end_date = date(
        year,
        12,
        31,
    ).isoformat()

    today_iso = today.isoformat()

    report: dict[str, Any] = {
        "status": "RUNNING",
        "base_url": BASE_URL,
        "suffix": suffix,
        "started_at": (
            datetime.now().isoformat(
                timespec="seconds"
            )
        ),
        "steps": [],
        "ids": {},
        "audit_verified": [],
    }

    limited_user_id: int | None = None

    def passed(
        name: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        item: dict[str, Any] = {
            "step": name,
            "status": "PASSED",
        }

        if details:
            item.update(details)

        report["steps"].append(item)
        print(f"[OK] {name}")

    try:
        # ----------------------------------------------------
        # 1. Salud y autenticación
        # ----------------------------------------------------
        health = http(
            "GET",
            "/health",
        )

        assert_equal(
            health.get("status"),
            "ok",
            "La API no reporta estado ok",
        )

        assert_equal(
            health.get("database"),
            "connected",
            "La API no reporta DB conectada",
        )

        passed("health")

        http(
            "GET",
            "/api/estudiantes",
            expected=(401,),
        )

        passed(
            "401 sin token en endpoint protegido"
        )

        login = http(
            "POST",
            "/api/auth/login",
            form_body={
                "username": USERNAME,
                "password": PASSWORD,
            },
        )

        token = login["access_token"]

        me = http(
            "GET",
            "/api/auth/me",
            token=token,
        )

        actor_id = int(
            me["id_usuario"]
        )

        report["actor_id"] = actor_id
        report["actor_username"] = (
            me.get("username")
        )

        required_permissions = {
            "SEGURIDAD_VER",
            "SEGURIDAD_GESTIONAR",
            "ESTUDIANTES_VER",
            "ESTUDIANTES_GESTIONAR",
            "ACADEMICO_VER",
            "ACADEMICO_GESTIONAR",
            "FINANZAS_VER",
            "PRECIOS_GESTIONAR",
            "OBLIGACIONES_GESTIONAR",
            "PAGOS_REGISTRAR",
            "SOLVENCIAS_GENERAR",
            "REPORTES_VER",
            "AUDITORIA_VER",
        }

        current_permissions = (
            permission_names(me)
        )

        missing_permissions = sorted(
            required_permissions
            - current_permissions
        )

        if missing_permissions:
            raise E2EError(
                "El usuario E2E no tiene todos "
                "los permisos necesarios: "
                + ", ".join(
                    missing_permissions
                )
            )

        passed(
            "login + /auth/me + preflight permisos"
        )

        # ----------------------------------------------------
        # 2. RBAC real con usuario limitado
        # ----------------------------------------------------
        permisos = http(
            "GET",
            "/api/permisos",
            token=token,
        )

        estudiantes_ver_id = (
            find_permission_id(
                permisos,
                "ESTUDIANTES_VER",
            )
        )

        role_name = (
            f"E2E_VIEWER_{suffix}"
        )

        role = http(
            "POST",
            "/api/roles",
            token=token,
            json_body={
                "nombre": role_name,
                "descripcion": (
                    "Rol temporal de prueba E2E"
                ),
            },
            expected=(201,),
        )

        role_id = int(
            role["id_rol"]
        )

        report["ids"]["role"] = role_id

        role = http(
            "PUT",
            f"/api/roles/{role_id}/permisos",
            token=token,
            json_body={
                "ids_permiso": [
                    estudiantes_ver_id
                ]
            },
        )

        role_perm_names = {
            item["nombre"]
            for item in role.get(
                "permisos",
                [],
            )
        }

        assert_equal(
            role_perm_names,
            {"ESTUDIANTES_VER"},
            "El rol E2E no quedó con "
            "el permiso esperado",
        )

        employee = http(
            "POST",
            "/api/empleados",
            token=token,
            json_body={
                "nombres": "E2E",
                "apellidos": (
                    f"Viewer {suffix}"
                ),
                "cargo": "Prueba E2E",
            },
            expected=(201,),
        )

        employee_id = int(
            employee["id_empleado"]
        )

        report["ids"]["employee"] = (
            employee_id
        )

        limited_username = (
            f"e2e_viewer_{suffix}".lower()
        )

        limited_password = (
            f"E2E!Viewer_{suffix}_A1"
        )

        limited_user = http(
            "POST",
            "/api/usuarios",
            token=token,
            json_body={
                "id_empleado": employee_id,
                "username": limited_username,
                "password": limited_password,
                "ids_rol": [role_id],
            },
            expected=(201,),
        )

        limited_user_id = int(
            limited_user["id_usuario"]
        )

        report["ids"]["limited_user"] = (
            limited_user_id
        )

        limited_login = http(
            "POST",
            "/api/auth/login",
            form_body={
                "username": limited_username,
                "password": limited_password,
            },
        )

        limited_token = (
            limited_login["access_token"]
        )

        limited_me = http(
            "GET",
            "/api/auth/me",
            token=limited_token,
        )

        limited_permissions = (
            permission_names(
                limited_me
            )
        )

        assert_equal(
            limited_permissions,
            {"ESTUDIANTES_VER"},
            "El usuario limitado no tiene "
            "exactamente el permiso esperado",
        )

        http(
            "GET",
            "/api/estudiantes",
            token=limited_token,
        )

        forbidden_student = {
            "codigo_estudiante":
                f"E2E-FORBIDDEN-{suffix}",
            "nombres": "No",
            "apellidos": "Debe Crearse",
        }

        http(
            "POST",
            "/api/estudiantes",
            token=limited_token,
            json_body=forbidden_student,
            expected=(403,),
        )

        http(
            "GET",
            "/api/auditoria",
            token=limited_token,
            expected=(403,),
        )

        passed(
            "RBAC: lectura permitida y "
            "escritura/auditoría denegadas"
        )

        # ----------------------------------------------------
        # 3. Catálogo académico
        # ----------------------------------------------------
        ciclo = http(
            "POST",
            "/api/ciclos",
            token=token,
            json_body={
                "nombre": (
                    f"E2E Ciclo {suffix}"
                ),
                "fecha_inicio": start_date,
                "fecha_fin": end_date,
                "estado": "PLANIFICADO",
            },
            expected=(201,),
        )

        ciclo_id = int(
            ciclo["id_ciclo"]
        )

        report["ids"]["ciclo"] = (
            ciclo_id
        )

        carrera = http(
            "POST",
            "/api/carreras",
            token=token,
            json_body={
                "nombre": (
                    f"E2E Carrera {suffix}"
                ),
                "descripcion": (
                    "Carrera generada por E2E"
                ),
            },
            expected=(201,),
        )

        carrera_id = int(
            carrera["id_carrera"]
        )

        report["ids"]["carrera"] = (
            carrera_id
        )

        carrera_ciclo = http(
            "POST",
            "/api/carrera-ciclos",
            token=token,
            json_body={
                "id_carrera": carrera_id,
                "id_ciclo": ciclo_id,
                "nombre_comercial": (
                    f"E2E Programa {suffix}"
                ),
            },
            expected=(201,),
        )

        carrera_ciclo_id = int(
            carrera_ciclo[
                "id_carrera_ciclo"
            ]
        )

        report["ids"][
            "carrera_ciclo"
        ] = carrera_ciclo_id

        grado = http(
            "POST",
            "/api/grados",
            token=token,
            json_body={
                "id_carrera_ciclo":
                    carrera_ciclo_id,
                "nombre": (
                    f"E2E Grado {suffix}"
                ),
                "nivel_orden": 1,
            },
            expected=(201,),
        )

        grado_id = int(
            grado["id_grado"]
        )

        report["ids"]["grado"] = (
            grado_id
        )

        passed(
            "catálogo académico"
        )

        # ----------------------------------------------------
        # 4. Estudiante e inscripción
        # ----------------------------------------------------
        student_code = (
            f"E2E-{suffix}"
        )

        student = http(
            "POST",
            "/api/estudiantes",
            token=token,
            json_body={
                "codigo_estudiante":
                    student_code,
                "nombres": "Estudiante",
                "apellidos": (
                    f"E2E {suffix}"
                ),
            },
            expected=(201,),
        )

        student_id = int(
            student["id_estudiante"]
        )

        report["ids"]["student"] = (
            student_id
        )

        inscripcion = http(
            "POST",
            "/api/inscripciones",
            token=token,
            json_body={
                "id_estudiante":
                    student_id,
                "id_carrera_ciclo":
                    carrera_ciclo_id,
                "id_grado": grado_id,
                "tipo": "NUEVA",
                "observaciones":
                    "Inscripción E2E",
            },
            expected=(201,),
        )

        inscription_id = int(
            inscripcion[
                "id_inscripcion"
            ]
        )

        report["ids"][
            "inscription"
        ] = inscription_id

        assert_equal(
            inscripcion["estado"],
            "ACTIVA",
            "La inscripción E2E no "
            "quedó ACTIVA",
        )

        passed(
            "estudiante + inscripción"
        )

        # ----------------------------------------------------
        # 5. Precio y primera obligación
        # ----------------------------------------------------
        price = http(
            "POST",
            "/api/precios",
            token=token,
            json_body={
                "id_carrera_ciclo":
                    carrera_ciclo_id,
                "tipo": "INSCRIPCION",
                "concepto": (
                    f"Inscripción E2E {suffix}"
                ),
                "monto": "100.00",
                "fecha_inicio":
                    start_date,
                "fecha_fin": end_date,
            },
            expected=(201,),
        )

        price_id = int(
            price["id_precio"]
        )

        report["ids"]["price"] = (
            price_id
        )

        obligation_1 = http(
            "POST",
            "/api/obligaciones/desde-precio",
            token=token,
            json_body={
                "id_inscripcion":
                    inscription_id,
                "id_precio": price_id,
                "fecha_vencimiento":
                    today_iso,
            },
            expected=(201,),
        )

        obligation_1_id = int(
            obligation_1[
                "id_obligacion"
            ]
        )

        report["ids"][
            "obligation_from_price"
        ] = obligation_1_id

        assert_equal(
            obligation_1["estado"],
            "PENDIENTE",
            "La obligación inicial no "
            "quedó PENDIENTE",
        )

        assert_equal(
            as_decimal(
                obligation_1["saldo"]
            ),
            Decimal("100.00"),
            "Saldo inicial incorrecto",
        )

        passed(
            "precio + obligación desde precio"
        )

        # ----------------------------------------------------
        # 6. Pago manual + aplicación + recibo
        # ----------------------------------------------------
        payment = http(
            "POST",
            "/api/pagos",
            token=token,
            json_body={
                "id_estudiante":
                    student_id,
                "monto": "100.00",
                "metodo": "EFECTIVO",
                "referencia":
                    f"E2E-{suffix}",
                "observaciones":
                    "Pago manual E2E",
            },
            expected=(201,),
        )

        payment_id = int(
            payment["id_pago"]
        )

        report["ids"][
            "manual_payment"
        ] = payment_id

        assert_equal(
            payment.get("id_usuario"),
            actor_id,
            "El pago no conserva "
            "id_usuario del actor",
        )

        application = http(
            "POST",
            (
                f"/api/pagos/"
                f"{payment_id}/aplicaciones"
            ),
            token=token,
            json_body={
                "id_obligacion":
                    obligation_1_id,
                "monto": "100.00",
            },
            expected=(201,),
        )

        application_id = int(
            application[
                "id_aplicacion"
            ]
        )

        report["ids"][
            "payment_application"
        ] = application_id

        applications = http(
            "GET",
            (
                f"/api/pagos/"
                f"{payment_id}/aplicaciones"
            ),
            token=token,
        )

        assert_true(
            any(
                int(item["id_aplicacion"])
                == application_id
                for item in applications
            ),
            "La aplicación del pago "
            "no aparece en el listado",
        )

        obligation_1 = http(
            "GET",
            (
                "/api/obligaciones/"
                f"{obligation_1_id}"
            ),
            token=token,
        )

        assert_equal(
            obligation_1["estado"],
            "PAGADA",
            "La primera obligación "
            "no quedó PAGADA",
        )

        assert_equal(
            as_decimal(
                obligation_1["saldo"]
            ),
            Decimal("0.00"),
            "La primera obligación "
            "no quedó con saldo cero",
        )

        receipt_1 = http(
            "POST",
            (
                f"/api/pagos/"
                f"{payment_id}/recibo"
            ),
            token=token,
        )

        receipt_2 = http(
            "POST",
            (
                f"/api/pagos/"
                f"{payment_id}/recibo"
            ),
            token=token,
        )

        receipt_id = int(
            receipt_1["id_recibo"]
        )

        report["ids"]["receipt"] = (
            receipt_id
        )

        assert_equal(
            int(receipt_2["id_recibo"]),
            receipt_id,
            "La generación de recibo "
            "no fue idempotente",
        )

        passed(
            "pago manual + aplicación "
            "+ recibo idempotente"
        )

        # ----------------------------------------------------
        # 7. Pago automático y saldo a favor
        # ----------------------------------------------------
        automatic = http(
            "POST",
            "/api/pagos/automatico",
            token=token,
            json_body={
                "id_estudiante":
                    student_id,
                "monto": "30.00",
                "metodo": "EFECTIVO",
                "referencia":
                    f"E2E-AUTO-{suffix}",
                "observaciones":
                    "Pago automático E2E",
            },
            expected=(201,),
        )

        automatic_payment = (
            automatic["pago"]
        )

        automatic_payment_id = int(
            automatic_payment["id_pago"]
        )

        report["ids"][
            "automatic_payment"
        ] = automatic_payment_id

        assert_equal(
            automatic_payment.get(
                "id_usuario"
            ),
            actor_id,
            "El pago automático no "
            "conserva id_usuario del actor",
        )

        credit = automatic.get(
            "saldo_favor"
        )

        assert_true(
            credit is not None,
            "El pago automático sin deuda "
            "pendiente no generó saldo a favor",
        )

        credit_id = int(
            credit["id_saldo_favor"]
        )

        report["ids"][
            "saldo_favor"
        ] = credit_id

        assert_equal(
            as_decimal(
                credit[
                    "monto_disponible"
                ]
            ),
            Decimal("30.00"),
            "Saldo a favor inicial incorrecto",
        )

        obligation_2 = http(
            "POST",
            "/api/obligaciones/manual",
            token=token,
            json_body={
                "id_inscripcion":
                    inscription_id,
                "concepto": (
                    f"Constancia E2E {suffix}"
                ),
                "tipo_obligacion":
                    "CONSTANCIA",
                "periodo": str(year),
                "fecha_vencimiento":
                    today_iso,
                "monto_bruto": "30.00",
            },
            expected=(201,),
        )

        obligation_2_id = int(
            obligation_2[
                "id_obligacion"
            ]
        )

        report["ids"][
            "manual_obligation"
        ] = obligation_2_id

        apply_credit = http(
            "POST",
            (
                "/api/saldos-favor/"
                f"{credit_id}/aplicar"
            ),
            token=token,
            json_body={
                "id_obligacion":
                    obligation_2_id,
                "monto": "30.00",
            },
        )

        assert_equal(
            as_decimal(
                apply_credit[
                    "monto_disponible"
                ]
            ),
            Decimal("0.00"),
            "El saldo a favor no quedó agotado",
        )

        obligation_2 = http(
            "GET",
            (
                "/api/obligaciones/"
                f"{obligation_2_id}"
            ),
            token=token,
        )

        assert_equal(
            obligation_2["estado"],
            "PAGADA",
            "La obligación pagada con "
            "saldo a favor no quedó PAGADA",
        )

        assert_equal(
            as_decimal(
                obligation_2["saldo"]
            ),
            Decimal("0.00"),
            "La segunda obligación "
            "no quedó con saldo cero",
        )

        passed(
            "pago automático + saldo a favor "
            "+ aplicación"
        )

        # ----------------------------------------------------
        # 8. Estado de cuenta
        # ----------------------------------------------------
        statement = http(
            "GET",
            (
                "/api/reportes/estado-cuenta/"
                f"{student_id}"
            ),
            token=token,
            params={
                "id_inscripcion":
                    inscription_id
            },
        )

        obligation_ids = {
            int(item["id_obligacion"])
            for item in statement
            if item.get(
                "id_obligacion"
            ) is not None
        }

        assert_true(
            obligation_1_id
            in obligation_ids,
            "El estado de cuenta no incluye "
            "la primera obligación",
        )

        assert_true(
            obligation_2_id
            in obligation_ids,
            "El estado de cuenta no incluye "
            "la segunda obligación",
        )

        passed(
            "estado de cuenta"
        )

        # ----------------------------------------------------
        # 9. Evaluación y solvencia
        # ----------------------------------------------------
        evaluation = http(
            "POST",
            "/api/evaluaciones",
            token=token,
            json_body={
                "id_ciclo": ciclo_id,
                "nombre": (
                    f"E2E Evaluación {suffix}"
                ),
                "fecha_evaluacion":
                    today_iso,
                "fecha_corte_finanzas":
                    today_iso,
            },
            expected=(201,),
        )

        evaluation_id = int(
            evaluation["id_evaluacion"]
        )

        report["ids"][
            "evaluation"
        ] = evaluation_id

        solvency = http(
            "POST",
            "/api/solvencias/generar",
            token=token,
            json_body={
                "id_estudiante":
                    student_id,
                "id_inscripcion":
                    inscription_id,
                "id_evaluacion":
                    evaluation_id,
            },
            expected=(201,),
        )

        solvency_id = int(
            solvency["id_solvencia"]
        )

        report["ids"][
            "solvency"
        ] = solvency_id

        assert_equal(
            solvency["estado"],
            "SOLVENTE",
            "El estudiante E2E debería "
            "estar SOLVENTE",
        )

        assert_equal(
            as_decimal(
                solvency["saldo_corte"]
            ),
            Decimal("0.00"),
            "La solvencia no quedó "
            "con saldo_corte cero",
        )

        verified_solvency = http(
            "GET",
            (
                "/api/solvencias/verificar/"
                f"{solvency['codigo_verificacion']}"
            ),
            token=token,
        )

        assert_equal(
            int(
                verified_solvency[
                    "id_solvencia"
                ]
            ),
            solvency_id,
            "La verificación por código "
            "no devolvió la solvencia creada",
        )

        duplicate_solvency = http(
            "POST",
            "/api/solvencias/generar",
            token=token,
            json_body={
                "id_estudiante":
                    student_id,
                "id_inscripcion":
                    inscription_id,
                "id_evaluacion":
                    evaluation_id,
            },
            expected=(201,),
        )

        assert_equal(
            int(
                duplicate_solvency[
                    "id_solvencia"
                ]
            ),
            solvency_id,
            "La generación de solvencia "
            "no fue idempotente",
        )

        passed(
            "evaluación + solvencia "
            "+ verificación + idempotencia"
        )

        # ----------------------------------------------------
        # 10. Auditoría
        # ----------------------------------------------------
        audit_checks = [
            (
                "CREAR_ROL",
                role_id,
            ),
            (
                "REEMPLAZAR_PERMISOS_ROL",
                role_id,
            ),
            (
                "CREAR_USUARIO",
                limited_user_id,
            ),
            (
                "CREAR_INSCRIPCION",
                inscription_id,
            ),
            (
                "CREAR_OBLIGACION_DESDE_PRECIO",
                obligation_1_id,
            ),
            (
                "REGISTRAR_PAGO",
                payment_id,
            ),
            (
                "APLICAR_PAGO",
                application_id,
            ),
            (
                "GENERAR_RECIBO",
                receipt_id,
            ),
            (
                "REGISTRAR_PAGO_AUTOMATICO",
                automatic_payment_id,
            ),
            (
                "CREAR_OBLIGACION_MANUAL",
                obligation_2_id,
            ),
            (
                "APLICAR_SALDO_FAVOR",
                credit_id,
            ),
            (
                "GENERAR_SOLVENCIA",
                solvency_id,
            ),
        ]

        for action, record_id in audit_checks:
            audit_event(
                token,
                accion=action,
                id_registro=record_id,
                actor_id=actor_id,
            )

            report[
                "audit_verified"
            ].append(
                {
                    "accion": action,
                    "id_registro":
                        record_id,
                }
            )

        passed(
            "auditoría transversal"
        )

        # ----------------------------------------------------
        # 11. Reportes
        # ----------------------------------------------------
        http(
            "GET",
            "/api/reportes/dashboard",
            token=token,
        )

        http(
            "GET",
            "/api/reportes/deuda-por-grado",
            token=token,
        )

        http(
            "GET",
            "/api/reportes/deuda-por-estudiante",
            token=token,
            params={
                "buscar": student_code,
                "limit": 20,
            },
        )

        http(
            "GET",
            "/api/reportes/estudiantes-insolventes",
            token=token,
            params={
                "buscar": student_code,
                "limit": 20,
            },
        )

        passed(
            "reportes financieros"
        )

        # ----------------------------------------------------
        # 12. Desactivar usuario E2E limitado
        # ----------------------------------------------------
        http(
            "PATCH",
            (
                "/api/usuarios/"
                f"{limited_user_id}/estado"
            ),
            token=token,
            json_body={
                "estado": "INACTIVO"
            },
        )

        passed(
            "desactivación del usuario "
            "limitado E2E"
        )

        report["status"] = "PASSED"
        report["finished_at"] = (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )

        output = Path(
            f"e2e_result_{suffix}.json"
        )

        output.write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        print()
        print(
            "=================================="
        )
        print(
            "E2E BACKEND: PASSED"
        )
        print(
            "=================================="
        )
        print(
            f"Reporte: {output}"
        )

        return 0

    except Exception as exc:
        report["status"] = "FAILED"
        report["finished_at"] = (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )
        report["error"] = str(exc)

        output = Path(
            f"e2e_result_{suffix}.json"
        )

        output.write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        print()
        print(
            "=================================="
        )
        print(
            "E2E BACKEND: FAILED"
        )
        print(
            "=================================="
        )
        print(
            f"Error: {exc}"
        )
        print(
            f"Reporte parcial: {output}"
        )

        if os.getenv(
            "E2E_TRACEBACK"
        ) == "1":
            traceback.print_exc()

        return 1


if __name__ == "__main__":
    sys.exit(main())
