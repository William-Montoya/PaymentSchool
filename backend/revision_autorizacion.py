from pathlib import Path
import ast

ROUTERS = Path("app/api/routers")

METODOS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
}

def nombre_llamada(node):
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        return node.attr

    return None

def ruta_decorador(decorator):
    if not isinstance(decorator, ast.Call):
        return None

    func = decorator.func

    if not isinstance(func, ast.Attribute):
        return None

    if func.attr not in METODOS:
        return None

    if not (
        isinstance(func.value, ast.Name)
        and func.value.id == "router"
    ):
        return None

    ruta = ""

    if decorator.args:
        arg = decorator.args[0]

        if isinstance(arg, ast.Constant):
            ruta = str(arg.value)

    return func.attr.upper(), ruta

def permisos_funcion(func):
    permisos = []

    for node in ast.walk(func):
        if not isinstance(node, ast.Call):
            continue

        if nombre_llamada(node.func) != "require_permission":
            continue

        if not node.args:
            continue

        try:
            permiso = ast.unparse(node.args[0])
        except Exception:
            permiso = "<no identificado>"

        permisos.append(permiso)

    return sorted(set(permisos))

def auth_directo(func):
    encontrados = set()

    for node in ast.walk(func):
        if isinstance(node, ast.Name):
            if node.id in {
                "get_current_user",
                "CurrentUser",
            }:
                encontrados.add(node.id)

    return sorted(encontrados)

print("=== REVISION FINAL DE AUTORIZACION ===")
print()

for archivo in sorted(ROUTERS.glob("*.py")):
    try:
        contenido = archivo.read_text(
            encoding="utf-8"
        )
        tree = ast.parse(contenido)
    except Exception as exc:
        print(
            f"[ERROR] {archivo}: {exc}"
        )
        continue

    endpoints = []

    for node in tree.body:
        if not isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            continue

        for decorator in node.decorator_list:
            ruta = ruta_decorador(decorator)

            if ruta is None:
                continue

            metodo, path = ruta

            endpoints.append(
                (
                    metodo,
                    path,
                    node.name,
                    permisos_funcion(node),
                    auth_directo(node),
                )
            )

    if not endpoints:
        continue

    print(f"--- {archivo} ---")

    for (
        metodo,
        path,
        funcion,
        permisos,
        autenticacion,
    ) in endpoints:

        permisos_txt = (
            ", ".join(permisos)
            if permisos
            else "NINGUNO"
        )

        auth_txt = (
            ", ".join(autenticacion)
            if autenticacion
            else "NINGUNO"
        )

        print(
            f"{metodo:6} "
            f"{path or '/':35} "
            f"{funcion}"
        )
        print(
            f"       permiso: {permisos_txt}"
        )
        print(
            f"       auth directo: {auth_txt}"
        )

    print()
