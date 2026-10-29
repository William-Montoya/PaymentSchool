from sqlalchemy import inspect

from app.core.database import Base
import app.models


print("=== ÍNDICES SQLALCHEMY ===")

for table_name, table in sorted(Base.metadata.tables.items()):
    print(f"\nTabla: {table_name}")

    indexes = sorted(table.indexes, key=lambda index: index.name or "")

    if not indexes:
        print("  └─ Sin índices declarados")

    for index in indexes:
        columns = ", ".join(column.name for column in index.columns)

        print(f"  └─ {index.name}")
        print(f"      columnas: {columns}")
        print(f"      unique: {index.unique}")

        if index.dialect_options:
            print(f"      dialect_options: {index.dialect_options}")