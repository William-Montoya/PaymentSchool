from sqlalchemy import inspect

from app.core.database import Base
import app.models


print("=== VALIDACIÓN DE RELACIONES ===\n")

for mapper in Base.registry.mappers:
    modelo = mapper.class_
    inspector = inspect(modelo)

    print(f"Modelo: {modelo.__name__}")

    for relationship in inspector.relationships:
        print(
            f"  └─ {relationship.key} -> "
            f"{relationship.mapper.class_.__name__}"
        )

    print()