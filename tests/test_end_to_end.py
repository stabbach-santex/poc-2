"""
Tests end-to-end del sistema completo
"""

import pytest
import requests
import time
import subprocess
import sys
import os

# Configuración
API_URL = "http://localhost:8000"
TIMEOUT = 30


def is_api_running():
    """Verifica si la API está corriendo"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


@pytest.fixture(scope="module")
def api_server():
    """
    Fixture que asegura que el servidor esté corriendo.
    Si no está corriendo, lo inicia.
    """
    if not is_api_running():
        pytest.skip("API no está corriendo. Ejecutar ./run_backend.sh primero")
    
    yield
    
    # Cleanup (si iniciamos el servidor, detenerlo)
    # En este caso, asumimos que el servidor ya está corriendo


def test_health_endpoint(api_server):
    """Test del endpoint /health"""
    response = requests.get(f"{API_URL}/health", timeout=5)
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]


def test_schema_endpoint(api_server):
    """Test del endpoint /schema"""
    response = requests.get(f"{API_URL}/schema", timeout=5)
    
    assert response.status_code == 200
    data = response.json()
    assert "tables" in data
    assert "trucks" in data["tables"]
    assert "drivers" in data["tables"]
    assert "trips" in data["tables"]
    assert "telemetry" in data["tables"]
    assert "alerts" in data["tables"]


def test_query_endpoint_simple(api_server):
    """Test básico del endpoint /query"""
    payload = {
        "user": "test_user",
        "nl": "Lista de camiones"
    }
    
    response = requests.post(
        f"{API_URL}/query",
        json=payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura de respuesta
    assert "nl" in data
    assert "sql" in data
    assert "rows" in data
    assert "explanation" in data
    assert "execution_time_ms" in data
    assert "rows_count" in data
    
    # Verificar que el SQL es válido
    assert "SELECT" in data["sql"].upper()
    assert "LIMIT" in data["sql"].upper()
    
    # Verificar que no hay comandos peligrosos
    sql_upper = data["sql"].upper()
    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
    for keyword in dangerous_keywords:
        assert keyword not in sql_upper


def test_query_endpoint_alerts(api_server):
    """Test query sobre alertas"""
    payload = {
        "user": "test_user",
        "nl": "Mostrar las últimas alertas críticas"
    }
    
    response = requests.post(
        f"{API_URL}/query",
        json=payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "alerts" in data["sql"].lower()
    assert data["rows_count"] >= 0


def test_query_endpoint_trips(api_server):
    """Test query sobre viajes"""
    payload = {
        "user": "test_user",
        "nl": "¿Cuántos viajes finalizados hubo?"
    }
    
    response = requests.post(
        f"{API_URL}/query",
        json=payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "trips" in data["sql"].lower()


def test_query_endpoint_performance(api_server):
    """Test de performance - debe responder en < 5s"""
    payload = {
        "user": "test_user",
        "nl": "Lista de camiones"
    }
    
    start_time = time.time()
    response = requests.post(
        f"{API_URL}/query",
        json=payload,
        timeout=TIMEOUT
    )
    elapsed_time = time.time() - start_time
    
    assert response.status_code == 200
    assert elapsed_time < 5.0  # Debe responder en menos de 5 segundos


def test_query_endpoint_invalid_sql_injection(api_server):
    """Test que el validador previene SQL injection"""
    payload = {
        "user": "test_user",
        "nl": "DROP TABLE trucks"
    }
    
    response = requests.post(
        f"{API_URL}/query",
        json=payload,
        timeout=TIMEOUT
    )
    
    # Puede retornar 400 (validación) o 200 con SQL seguro
    if response.status_code == 200:
        data = response.json()
        # Verificar que no se generó un DROP
        assert "DROP" not in data["sql"].upper()


def test_query_endpoint_multiple_queries(api_server):
    """Test múltiples queries consecutivas"""
    queries = [
        "Lista de camiones",
        "Alertas críticas",
        "Viajes finalizados"
    ]
    
    for query in queries:
        payload = {
            "user": "test_user",
            "nl": query
        }
        
        response = requests.post(
            f"{API_URL}/query",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rows_count"] >= 0


def test_logs_endpoint(api_server):
    """Test del endpoint /logs"""
    # Primero hacer una query para generar un log
    payload = {
        "user": "test_user",
        "nl": "Lista de camiones"
    }
    requests.post(f"{API_URL}/query", json=payload, timeout=TIMEOUT)
    
    # Ahora obtener logs
    response = requests.get(f"{API_URL}/logs?limit=10", timeout=5)
    
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
