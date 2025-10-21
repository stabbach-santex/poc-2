"""
Validador de SQL para prevenir queries peligrosas y asegurar
que solo se ejecuten consultas SELECT seguras.
"""

import re
from typing import List, Set


# Tablas permitidas en el schema canónico
ALLOWED_TABLES = {"trucks", "drivers", "trips", "telemetry", "alerts"}

# Tokens prohibidos (comandos peligrosos)
BANNED_TOKENS = [
    ";DROP", ";DELETE", ";UPDATE", ";INSERT", ";ALTER", ";EXEC",
    "DROP ", "DELETE ", "UPDATE ", "INSERT ", "ALTER ", "EXEC ",
    "PRAGMA", "ATTACH", "DETACH", "CREATE ", "TRUNCATE",
    "--", "/*", "*/", "UNION ALL", "UNION SELECT"
]

# Columnas permitidas por tabla (para validación adicional)
ALLOWED_COLUMNS = {
    "trucks": {"truck_id", "plate", "model", "brand", "driver_id", "region", "status"},
    "drivers": {"driver_id", "name", "license"},
    "trips": {"trip_id", "truck_id", "origin", "destination", "start_time", "end_time", "distance_km", "status"},
    "telemetry": {"telemetry_id", "truck_id", "timestamp", "speed_kmh", "fuel_level", "engine_temp_c"},
    "alerts": {"alert_id", "truck_id", "timestamp", "alert_type", "severity", "description"}
}


class SQLValidationError(Exception):
    """Excepción para errores de validación SQL"""
    pass


def extract_tables_from_sql(sql: str) -> Set[str]:
    """
    Extrae nombres de tablas referenciadas en el SQL.
    Busca patrones como FROM table, JOIN table, etc.
    """
    sql_upper = sql.upper()
    tables = set()
    
    # Patrones para encontrar tablas
    patterns = [
        r'FROM\s+(\w+)',
        r'JOIN\s+(\w+)',
        r'INTO\s+(\w+)',
        r'UPDATE\s+(\w+)',
        r'TABLE\s+(\w+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, sql_upper)
        tables.update([m.lower() for m in matches])
    
    return tables


def validate_sql(sql: str, strict: bool = True) -> str:
    """
    Valida y sanitiza una consulta SQL.
    
    Args:
        sql: Consulta SQL a validar
        strict: Si True, aplica validaciones estrictas
    
    Returns:
        SQL validado y sanitizado (con LIMIT agregado si es necesario)
    
    Raises:
        SQLValidationError: Si el SQL no pasa las validaciones
    """
    
    if not sql or not sql.strip():
        raise SQLValidationError("SQL vacío")
    
    sql = sql.strip()
    sql_upper = sql.upper()
    
    # 1. Verificar que sea solo SELECT o WITH
    if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
        raise SQLValidationError(
            "Solo se permiten consultas SELECT o WITH. "
            f"La consulta comienza con: {sql[:20]}"
        )
    
    # 2. Verificar tokens prohibidos
    for banned in BANNED_TOKENS:
        if banned.upper() in sql_upper:
            raise SQLValidationError(
                f"Token prohibido detectado: '{banned}'. "
                "No se permiten comandos DML/DDL."
            )
    
    # 3. Verificar múltiples statements (detectar ; seguido de más SQL)
    # Permitir ; al final, pero no en medio
    sql_stripped = sql.rstrip(';').strip()
    if ';' in sql_stripped:
        raise SQLValidationError(
            "No se permiten múltiples statements SQL. "
            "Detectado ';' en medio de la consulta."
        )
    
    # 4. Extraer y validar tablas referenciadas
    referenced_tables = extract_tables_from_sql(sql)
    invalid_tables = referenced_tables - ALLOWED_TABLES
    
    if invalid_tables:
        raise SQLValidationError(
            f"Tablas no permitidas: {invalid_tables}. "
            f"Tablas válidas: {ALLOWED_TABLES}"
        )
    
    # 5. Verificar que al menos una tabla válida esté referenciada
    if strict and not referenced_tables:
        raise SQLValidationError(
            "No se detectaron tablas válidas en la consulta. "
            f"Tablas disponibles: {ALLOWED_TABLES}"
        )
    
    # 6. Agregar LIMIT si no existe (prevenir queries masivas)
    if "LIMIT" not in sql_upper:
        sql = sql.rstrip(';').strip() + " LIMIT 1000"
    
    # 7. Validar que el LIMIT no sea excesivo
    limit_match = re.search(r'LIMIT\s+(\d+)', sql_upper)
    if limit_match:
        limit_value = int(limit_match.group(1))
        if limit_value > 10000:
            raise SQLValidationError(
                f"LIMIT demasiado alto: {limit_value}. Máximo permitido: 10000"
            )
    
    # 8. Asegurar que termina con ;
    if not sql.endswith(';'):
        sql += ';'
    
    return sql


def validate_and_explain(sql: str) -> dict:
    """
    Valida SQL y retorna información detallada.
    
    Returns:
        dict con: valid (bool), sql (str sanitizado), errors (list), warnings (list)
    """
    result = {
        "valid": False,
        "sql": sql,
        "errors": [],
        "warnings": []
    }
    
    try:
        validated_sql = validate_sql(sql)
        result["valid"] = True
        result["sql"] = validated_sql
        
        # Agregar warnings si se hicieron modificaciones
        if "LIMIT" not in sql.upper():
            result["warnings"].append("Se agregó LIMIT 1000 automáticamente")
        
    except SQLValidationError as e:
        result["errors"].append(str(e))
    except Exception as e:
        result["errors"].append(f"Error inesperado: {str(e)}")
    
    return result


# Ejemplos de uso y tests
if __name__ == "__main__":
    print("🧪 Probando validador SQL...\n")
    
    test_cases = [
        # Casos válidos
        ("SELECT * FROM trucks", True),
        ("SELECT truck_id, COUNT(*) FROM alerts GROUP BY truck_id", True),
        ("SELECT t.*, d.name FROM trucks t JOIN drivers d ON t.driver_id = d.driver_id", True),
        
        # Casos inválidos
        ("DROP TABLE trucks", False),
        ("SELECT * FROM trucks; DELETE FROM trips", False),
        ("UPDATE trucks SET status = 'inactive'", False),
        ("SELECT * FROM invalid_table", False),
    ]
    
    for sql, should_pass in test_cases:
        result = validate_and_explain(sql)
        status = "✅" if result["valid"] == should_pass else "❌"
        print(f"{status} {sql[:50]}...")
        if result["errors"]:
            print(f"   Errors: {result['errors']}")
        if result["warnings"]:
            print(f"   Warnings: {result['warnings']}")
        print()
