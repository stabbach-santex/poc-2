"""
FastAPI Backend para LogiQ AI
Expone endpoint /query para procesar consultas en lenguaje natural.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os
import sys
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.lib.validate_sql import validate_sql, SQLValidationError
from backend.lib.gemini_client import GeminiClient


# Configuración
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.getenv("DB_PATH", os.path.join(PROJECT_ROOT, "data/logiq.db"))
LOG_PATH = os.getenv("LOG_PATH", os.path.join(PROJECT_ROOT, "logs/queries.log"))
PORT = int(os.getenv("PORT", 8000))

# Inicializar FastAPI
app = FastAPI(
    title="LogiQ AI API",
    description="API para consultar data warehouse logístico mediante lenguaje natural",
    version="1.0.0"
)

# CORS (permitir frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar cliente Gemini
gemini_client = GeminiClient()


# Modelos Pydantic
class QueryRequest(BaseModel):
    """Request para endpoint /query"""
    user: str
    nl: str  # natural language query


class QueryResponse(BaseModel):
    """Response del endpoint /query"""
    nl: str
    sql: str
    rows: List[Dict[str, Any]]
    explanation: str
    execution_time_ms: float
    rows_count: int


# Funciones auxiliares
def get_db_connection():
    """Obtiene conexión a SQLite"""
    if not os.path.exists(DB_PATH):
        raise HTTPException(
            status_code=500,
            detail=f"Base de datos no encontrada: {DB_PATH}. Ejecutar ./run_backend.sh primero."
        )
    return sqlite3.connect(DB_PATH)


def execute_sql(sql: str) -> List[Dict[str, Any]]:
    """
    Ejecuta SQL y retorna resultados como lista de dicts.
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # Para obtener resultados como dict
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        # Convertir Row objects a dicts
        result = [dict(row) for row in rows]
        return result
        
    finally:
        conn.close()


def log_query(user: str, nl: str, sql: str, exec_time_ms: float, rows_count: int, error: Optional[str] = None):
    """
    Registra query en archivo de log.
    """
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": user,
        "nl": nl,
        "sql": sql,
        "exec_time_ms": exec_time_ms,
        "rows_count": rows_count,
        "error": error
    }
    
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


# Endpoints
@app.get("/")
async def root():
    """Endpoint raíz - health check"""
    return {
        "service": "LogiQ AI API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "query": "POST /query",
            "health": "GET /health",
            "schema": "GET /schema"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trucks")
        count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "trucks_count": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/schema")
async def get_schema():
    """Retorna el schema canónico"""
    return {
        "tables": {
            "trucks": {
                "columns": ["truck_id", "plate", "model", "brand", "driver_id", "region", "status"],
                "primary_key": "truck_id"
            },
            "drivers": {
                "columns": ["driver_id", "name", "license"],
                "primary_key": "driver_id"
            },
            "trips": {
                "columns": ["trip_id", "truck_id", "origin", "destination", "start_time", "end_time", "distance_km", "status"],
                "primary_key": "trip_id",
                "foreign_keys": {"truck_id": "trucks.truck_id"}
            },
            "telemetry": {
                "columns": ["telemetry_id", "truck_id", "timestamp", "speed_kmh", "fuel_level", "engine_temp_c"],
                "primary_key": "telemetry_id",
                "foreign_keys": {"truck_id": "trucks.truck_id"}
            },
            "alerts": {
                "columns": ["alert_id", "truck_id", "timestamp", "alert_type", "severity", "description"],
                "primary_key": "alert_id",
                "foreign_keys": {"truck_id": "trucks.truck_id"}
            }
        }
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Endpoint principal: procesa consulta en lenguaje natural.
    
    Flujo:
    1. Recibir NL query
    2. Llamar Gemini para generar SQL
    3. Validar SQL
    4. Ejecutar SQL en SQLite
    5. Generar explicación
    6. Retornar resultados + log
    """
    
    start_time = time.time()
    user = request.user
    nl_query = request.nl
    
    sql = ""
    rows = []
    explanation = ""
    error_msg = None
    
    try:
        # Paso 1: Generar SQL desde lenguaje natural
        print(f"📝 NL Query: {nl_query}")
        sql = gemini_client.nl_to_sql(nl_query)
        print(f"🔍 Generated SQL: {sql}")
        
        # Paso 2: Validar SQL
        try:
            sql = validate_sql(sql, strict=True)
            print(f"✅ SQL validado")
        except SQLValidationError as e:
            raise HTTPException(
                status_code=400,
                detail=f"SQL inválido: {str(e)}"
            )
        
        # Paso 3: Ejecutar SQL
        rows = execute_sql(sql)
        print(f"📊 Resultados: {len(rows)} filas")
        
        # Paso 4: Generar explicación
        explanation = gemini_client.generate_explanation(nl_query, sql, rows)
        
        # Calcular tiempo de ejecución
        exec_time_ms = (time.time() - start_time) * 1000
        
        # Log exitoso
        log_query(user, nl_query, sql, exec_time_ms, len(rows))
        
        return QueryResponse(
            nl=nl_query,
            sql=sql,
            rows=rows,
            explanation=explanation,
            execution_time_ms=round(exec_time_ms, 2),
            rows_count=len(rows)
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        exec_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log con error
        log_query(user, nl_query, sql, exec_time_ms, 0, error_msg)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando query: {error_msg}"
        )


@app.get("/logs")
async def get_logs(limit: int = 50):
    """Retorna últimos logs de queries"""
    if not os.path.exists(LOG_PATH):
        return {"logs": []}
    
    logs = []
    with open(LOG_PATH, "r") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except:
                pass
    
    # Retornar últimos N logs
    return {"logs": logs[-limit:]}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Evento de inicio"""
    print("=" * 60)
    print("🚀 LogiQ AI API - Starting...")
    print("=" * 60)
    print(f"📁 Database: {DB_PATH}")
    print(f"📝 Logs: {LOG_PATH}")
    print(f"🔑 Gemini Mode: {'API' if not gemini_client.use_mock else 'Mock'}")
    print("=" * 60)
    
    # Verificar que la base de datos existe
    if not os.path.exists(DB_PATH):
        print("⚠️  WARNING: Base de datos no encontrada!")
        print("   Ejecutar: python3 scripts/generate_data.py && python3 scripts/load_data.py")
    else:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM trucks")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"✅ Base de datos conectada ({count} camiones)")
        except Exception as e:
            print(f"❌ Error conectando a base de datos: {e}")
    
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
