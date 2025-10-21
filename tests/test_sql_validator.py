"""
Tests para el validador de SQL
"""

import pytest
import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.lib.validate_sql import validate_sql, validate_and_explain, SQLValidationError


def test_valid_select():
    """Test SELECT válido"""
    sql = "SELECT * FROM trucks"
    result = validate_sql(sql)
    assert "SELECT" in result
    assert "LIMIT" in result  # Debe agregar LIMIT


def test_valid_select_with_limit():
    """Test SELECT con LIMIT ya incluido"""
    sql = "SELECT * FROM trucks LIMIT 10"
    result = validate_sql(sql)
    assert "LIMIT 10" in result


def test_valid_join():
    """Test JOIN válido"""
    sql = "SELECT t.*, d.name FROM trucks t JOIN drivers d ON t.driver_id = d.driver_id"
    result = validate_sql(sql)
    assert "JOIN" in result


def test_valid_with_clause():
    """Test WITH clause válido"""
    sql = "WITH temp AS (SELECT * FROM trips) SELECT * FROM temp"
    result = validate_sql(sql)
    assert "WITH" in result


def test_invalid_drop():
    """Test DROP no permitido"""
    sql = "DROP TABLE trucks"
    with pytest.raises(SQLValidationError) as exc_info:
        validate_sql(sql)
    assert "SELECT" in str(exc_info.value).upper() or "DROP" in str(exc_info.value).upper()


def test_invalid_delete():
    """Test DELETE no permitido"""
    sql = "DELETE FROM trucks WHERE truck_id = 'T001'"
    with pytest.raises(SQLValidationError) as exc_info:
        validate_sql(sql)
    assert "SELECT" in str(exc_info.value).upper() or "DELETE" in str(exc_info.value).upper()


def test_invalid_update():
    """Test UPDATE no permitido"""
    sql = "UPDATE trucks SET status = 'inactive'"
    with pytest.raises(SQLValidationError) as exc_info:
        validate_sql(sql)
    assert "SELECT" in str(exc_info.value).upper() or "UPDATE" in str(exc_info.value).upper()


def test_invalid_insert():
    """Test INSERT no permitido"""
    sql = "INSERT INTO trucks VALUES ('T999', 'ABC123')"
    with pytest.raises(SQLValidationError) as exc_info:
        validate_sql(sql)
    assert "SELECT" in str(exc_info.value).upper() or "INSERT" in str(exc_info.value).upper()


def test_invalid_multiple_statements():
    """Test múltiples statements no permitidos"""
    sql = "SELECT * FROM trucks; DELETE FROM trips"
    with pytest.raises(SQLValidationError) as exc_info:
        validate_sql(sql)
    assert "múltiples" in str(exc_info.value).lower() or "statement" in str(exc_info.value).lower()


def test_invalid_table():
    """Test tabla no permitida"""
    sql = "SELECT * FROM invalid_table"
    with pytest.raises(SQLValidationError) as exc_info:
        validate_sql(sql)
    assert "tabla" in str(exc_info.value).lower() or "permitida" in str(exc_info.value).lower()


def test_excessive_limit():
    """Test LIMIT excesivo"""
    sql = "SELECT * FROM trucks LIMIT 50000"
    with pytest.raises(SQLValidationError) as exc_info:
        validate_sql(sql)
    assert "limit" in str(exc_info.value).lower()


def test_validate_and_explain_valid():
    """Test función validate_and_explain con SQL válido"""
    sql = "SELECT * FROM trucks"
    result = validate_and_explain(sql)
    
    assert result["valid"] is True
    assert "SELECT" in result["sql"]
    assert len(result["errors"]) == 0


def test_validate_and_explain_invalid():
    """Test función validate_and_explain con SQL inválido"""
    sql = "DROP TABLE trucks"
    result = validate_and_explain(sql)
    
    assert result["valid"] is False
    assert len(result["errors"]) > 0


def test_empty_sql():
    """Test SQL vacío"""
    with pytest.raises(SQLValidationError) as exc_info:
        validate_sql("")
    assert "vacío" in str(exc_info.value).lower()


def test_sql_with_comments():
    """Test SQL con comentarios (no permitidos)"""
    sql = "SELECT * FROM trucks -- comment"
    with pytest.raises(SQLValidationError) as exc_info:
        validate_sql(sql)
    assert "prohibido" in str(exc_info.value).lower() or "--" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
