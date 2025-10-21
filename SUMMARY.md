# 📋 LogiQ AI - Resumen del Proyecto

## 🎯 Descripción General

**LogiQ AI** es un asistente conversacional que permite consultar un data warehouse logístico mediante lenguaje natural. Integra datos de 4 fuentes diferentes (Tera, Cloudfleet, Scania, Keeper), los normaliza a un schema canónico, y utiliza Gemini AI para convertir preguntas en SQL seguro.

---

## 🚀 Comandos Rápidos

### Instalación y Ejecución (3 comandos)

```bash
# 1. Setup: instalar dependencias
./setup.sh

# 2. Backend: cargar datos y levantar API
./run_backend.sh

# 3. Frontend: abrir UI (en otra terminal)
./run_frontend.sh
```

### Demo Completo

```bash
./demo/run_demo.sh
```

---

## 📡 Endpoints de la API

### Base URL
```
http://localhost:8000
```

### Endpoints Disponibles

#### 1. Health Check
```bash
GET /health

# Ejemplo:
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "trucks_count": 50
}
```

---

#### 2. Schema Canónico
```bash
GET /schema

# Ejemplo:
curl http://localhost:8000/schema
```

**Response:**
```json
{
  "tables": {
    "trucks": {
      "columns": ["truck_id", "plate", "model", "brand", "driver_id", "region", "status"],
      "primary_key": "truck_id"
    },
    ...
  }
}
```

---

#### 3. Query (Principal)
```bash
POST /query
Content-Type: application/json

{
  "user": "user_id",
  "nl": "pregunta en lenguaje natural"
}
```

**Ejemplo 1:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user": "demo_user",
    "nl": "¿Qué camión tuvo más alertas de temperatura en la última semana?"
  }'
```

**Response:**
```json
{
  "nl": "¿Qué camión tuvo más alertas de temperatura en la última semana?",
  "sql": "SELECT truck_id, COUNT(*) as alerts FROM alerts WHERE alert_type = 'temperature' AND timestamp >= datetime('now', '-7 days') GROUP BY truck_id ORDER BY alerts DESC LIMIT 5;",
  "rows": [
    {"truck_id": "TRUCK_042", "alerts": 15},
    {"truck_id": "TRUCK_023", "alerts": 12},
    ...
  ],
  "explanation": "El camión TRUCK_042 tuvo 15 alertas de temperatura en la última semana...",
  "execution_time_ms": 234.5,
  "rows_count": 5
}
```

---

#### 4. Logs
```bash
GET /logs?limit=50

# Ejemplo:
curl http://localhost:8000/logs?limit=10
```

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2025-10-21T13:15:30Z",
      "user": "demo_user",
      "nl": "Lista de camiones",
      "sql": "SELECT * FROM trucks LIMIT 1000;",
      "exec_time_ms": 45.2,
      "rows_count": 50,
      "error": null
    },
    ...
  ]
}
```

---

## 🎯 10 Queries Demo

### 1. Alertas de Temperatura
```
¿Qué camión tuvo más alertas de temperatura en la última semana?
```
**Resultado esperado**: Top 5 camiones con más alertas de tipo "temperature"

---

### 2. Consumo por Marca
```
Promedio de consumo por marca de camión en los últimos 30 días
```
**Resultado esperado**: AVG(fuel_level) agrupado por brand

---

### 3. Viajes Finalizados
```
¿Cuántos viajes finalizados hubo ayer?
```
**Resultado esperado**: COUNT de trips con status='finished' y fecha de ayer

---

### 4. Alertas Críticas
```
Mostrar las 10 últimas alertas críticas
```
**Resultado esperado**: 10 alertas con severity='critical' ordenadas por timestamp DESC

---

### 5. Camiones en Mantenimiento
```
Lista de camiones actualmente en mantenimiento
```
**Resultado esperado**: Camiones con status='maintenance'

---

### 6. Rutas con Retrasos
```
Top 5 rutas con más retrasos
```
**Resultado esperado**: Rutas (origin-destination) con mayor duración promedio

---

### 7. Top Conductor
```
¿Cuál es el conductor con más kilómetros recorridos este mes?
```
**Resultado esperado**: Conductor con mayor SUM(distance_km) en últimos 30 días

---

### 8. Alertas de Velocidad
```
Alertas de velocidad excesiva en la última semana
```
**Resultado esperado**: Alertas de tipo "speed" en últimos 7 días

---

### 9. Combustible Bajo
```
Camiones con nivel de combustible bajo (< 20%)
```
**Resultado esperado**: Camiones con fuel_level < 20

---

### 10. Viajes Largos por Región
```
Viajes más largos por región
```
**Resultado esperado**: Top viajes ordenados por distance_km, agrupados por región

---

## 📊 Schema Canónico

### Tabla: trucks
```sql
CREATE TABLE trucks (
    truck_id TEXT PRIMARY KEY,
    plate TEXT,
    model TEXT,
    brand TEXT,
    driver_id TEXT,
    region TEXT,
    status TEXT
);
```
**Registros**: 50 camiones

---

### Tabla: drivers
```sql
CREATE TABLE drivers (
    driver_id TEXT PRIMARY KEY,
    name TEXT,
    license TEXT
);
```
**Registros**: 60 conductores

---

### Tabla: trips
```sql
CREATE TABLE trips (
    trip_id TEXT PRIMARY KEY,
    truck_id TEXT,
    origin TEXT,
    destination TEXT,
    start_time TEXT,
    end_time TEXT,
    distance_km REAL,
    status TEXT,
    FOREIGN KEY (truck_id) REFERENCES trucks(truck_id)
);
```
**Registros**: 500 viajes

---

### Tabla: telemetry
```sql
CREATE TABLE telemetry (
    telemetry_id TEXT PRIMARY KEY,
    truck_id TEXT,
    timestamp TEXT,
    speed_kmh REAL,
    fuel_level REAL,
    engine_temp_c REAL,
    FOREIGN KEY (truck_id) REFERENCES trucks(truck_id)
);
```
**Registros**: 2000 registros (1000 de Cloudfleet + 1000 de Scania)

---

### Tabla: alerts
```sql
CREATE TABLE alerts (
    alert_id TEXT PRIMARY KEY,
    truck_id TEXT,
    timestamp TEXT,
    alert_type TEXT,
    severity TEXT,
    description TEXT,
    FOREIGN KEY (truck_id) REFERENCES trucks(truck_id)
);
```
**Registros**: 300 alertas

---

## 🧪 Tests

### Ejecutar Todos los Tests
```bash
source venv/bin/activate
pytest tests/ -v
```

### Tests Específicos

**Adapters:**
```bash
pytest tests/test_adapters.py -v
```

**SQL Validator:**
```bash
pytest tests/test_sql_validator.py -v
```

**End-to-End:**
```bash
# Primero iniciar el backend
./run_backend.sh

# En otra terminal:
pytest tests/test_end_to_end.py -v
```

---

## 🔧 Configuración

### Variables de Entorno (.env)

```bash
# API Keys (configurar al menos una)
GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_key_here

# BigQuery (opcional)
USE_BIGQUERY=false
# BQ_PROJECT=your-gcp-project
# BQ_DATASET=logiq_warehouse

# Configuración
PORT=8000
DB_PATH=data/logiq.db
LOG_PATH=logs/queries.log
```

### Modo Mock vs API Real

**Sin API Key (Modo Mock)**:
- Usa templates predefinidos para generar SQL
- Funcional para demo y desarrollo
- No requiere conexión a internet

**Con API Key (Modo Real)**:
- Usa Gemini AI para NL → SQL
- Mejor calidad de SQL generado
- Soporta queries más complejas

---

## 📁 Estructura de Archivos

```
logiq-ai-proto/
├── README.md                 # Documentación principal
├── SUMMARY.md               # Este archivo
├── TODO.md                  # Tareas pendientes
├── setup.sh                 # Script de instalación
├── run_backend.sh           # Iniciar backend
├── run_frontend.sh          # Iniciar frontend
├── .env                     # Variables de entorno
├── .gitignore              # Git ignore
│
├── data/                    # Datos y base de datos
│   ├── tera_trips.csv
│   ├── cloudfleet_positions.csv
│   ├── scania_metrics.csv
│   ├── keeper_alerts.csv
│   ├── master_trucks.csv
│   ├── master_drivers.csv
│   └── logiq.db            # SQLite database
│
├── adapters/               # Transformadores de datos
│   ├── __init__.py
│   ├── adapter_base.py
│   ├── tera_adapter.py
│   ├── cloudfleet_adapter.py
│   ├── scania_adapter.py
│   └── keeper_adapter.py
│
├── mappings/               # Configuraciones YAML
│   ├── tera_mapping.yaml
│   ├── cloudfleet_mapping.yaml
│   ├── scania_mapping.yaml
│   └── keeper_mapping.yaml
│
├── backend/                # FastAPI application
│   ├── app.py             # Aplicación principal
│   └── lib/
│       ├── __init__.py
│       ├── validate_sql.py
│       └── gemini_client.py
│
├── frontend/               # Streamlit UI
│   └── streamlit_app.py
│
├── scripts/                # Scripts de utilidad
│   ├── generate_data.py   # Generar CSVs simulados
│   └── load_data.py       # Cargar datos en SQLite
│
├── tests/                  # Tests automatizados
│   ├── test_adapters.py
│   ├── test_sql_validator.py
│   └── test_end_to_end.py
│
├── demo/                   # Assets de demostración
│   ├── run_demo.sh
│   └── demo_script.md
│
├── slides/                 # Presentación
│   └── pitch.md
│
└── logs/                   # Logs de queries
    ├── queries.log
    └── backend.log
```

---

## 🔒 Seguridad

### Validador SQL

**Reglas Implementadas:**
1. ✅ Solo permite `SELECT` y `WITH`
2. ❌ Bloquea `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `EXEC`
3. ✅ Whitelist de tablas (solo schema canónico)
4. ✅ Auto-LIMIT 1000 (previene queries masivas)
5. ❌ Detecta múltiples statements (`;` en medio)
6. ❌ Bloquea comentarios SQL (`--`, `/*`)
7. ✅ Límite máximo: 10,000 filas

### Auditoría

Todos los queries se registran en `logs/queries.log`:
- Timestamp
- Usuario
- Query original (NL)
- SQL generado
- Tiempo de ejecución
- Número de resultados
- Errores (si los hay)

---

## 📈 Performance

### Métricas Esperadas

**Tiempo de Respuesta:**
- Query simple: < 500ms
- Query con JOIN: < 1s
- Query compleja: < 2s
- Objetivo: < 5s (criterio de aceptación)

**Capacidad:**
- 10K queries/día
- 100 usuarios concurrentes
- Base de datos: 2500+ registros

**Recursos:**
- RAM: ~200MB
- CPU: < 10% en idle
- Disco: ~50MB (SQLite)

---

## 🐛 Troubleshooting

### Backend no inicia

**Error**: `Base de datos no encontrada`
```bash
# Solución:
python3 scripts/generate_data.py
python3 scripts/load_data.py
```

---

### Frontend no conecta

**Error**: `No se puede conectar al backend`
```bash
# Verificar que el backend esté corriendo:
curl http://localhost:8000/health

# Si no responde, iniciar backend:
./run_backend.sh
```

---

### Gemini API no funciona

**Error**: `Error configurando Gemini`
```bash
# Verificar API key en .env:
cat .env | grep GEMINI_API_KEY

# Si no está configurada, el sistema usa modo mock automáticamente
```

---

### Tests fallan

**Error**: `API no está corriendo`
```bash
# Para tests e2e, primero iniciar backend:
./run_backend.sh

# En otra terminal:
pytest tests/test_end_to_end.py -v
```

---

## 🚀 Próximos Pasos

### Para Desarrollo

1. **Configurar API Key**:
   - Obtener Gemini API key
   - Agregar a `.env`
   - Reiniciar backend

2. **Agregar Más Datos**:
   - Editar `scripts/generate_data.py`
   - Aumentar `NUM_TRIPS`, `NUM_TELEMETRY`, etc.
   - Re-ejecutar `load_data.py`

3. **Personalizar Queries**:
   - Editar `backend/lib/gemini_client.py`
   - Agregar más ejemplos en `SYSTEM_PROMPT`
   - Mejorar templates en `_mock_nl_to_sql`

### Para Producción

1. **Integración Real**:
   - Conectar APIs de Tera, Cloudfleet, Scania, Keeper
   - Implementar ETL automatizado
   - Sincronización en tiempo real

2. **Escalabilidad**:
   - Migrar a BigQuery
   - Implementar caché (Redis)
   - Load balancing

3. **Seguridad**:
   - Autenticación (OAuth2/JWT)
   - Rate limiting
   - Encriptación de datos sensibles

4. **Monitoreo**:
   - Prometheus + Grafana
   - Alertas automáticas
   - Logging centralizado

---

## 📞 Soporte

### Documentación
- `README.md` - Guía principal
- `demo/demo_script.md` - Script de presentación
- `slides/pitch.md` - Presentación completa

### Contacto
- 📧 Email: logiq-ai@santex.com
- 💼 LinkedIn: /logiq-ai
- 🌐 Web: logiq-ai.demo

---

## 📄 Licencia

MIT License - Ver LICENSE file

---

**Desarrollado para GLAC Hackathon 2025** 🚀
