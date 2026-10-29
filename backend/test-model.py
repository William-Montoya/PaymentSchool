from app.core.database import Base
import app.models


print("=== ESQUEMA ===")
print(Base.metadata.schema)

print("\n=== TABLAS REGISTRADAS ===")

for tabla in Base.metadata.tables.keys():
    print(tabla)

print("\n=== TOTAL DE TABLAS ===")
print(len(Base.metadata.tables))