# 📡 LogiQ AI - API Documentation

## Base URL

```
http://localhost:8000
```

---

## Authentication

Currently, no authentication is required for the MVP. For production, implement OAuth2/JWT.

---

## Endpoints

### 1. Root / Health Check

#### `GET /`

Returns basic API information.

**Request:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "service": "LogiQ AI API",
  "status": "running",
  "version": "1.0.0",
  "endpoints": {
    "query": "POST /query",
    "health": "GET /health",
    "schema": "GET /schema"
  }
}
```

---

### 2. Health Check

#### `GET /health`

Verifies API and database connectivity.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (Healthy):**
```json
{
  "status": "healthy",
  "database": "connected",
  "trucks_count": 50
}
```

**Response (Unhealthy):**
```json
{
  "status": "unhealthy",
  "error": "Database connection failed"
}
```

---

### 3. Schema Information

#### `GET /schema`

Returns the canonical schema with all tables and columns.

**Request:**
```bash
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
```

---

### 4. Query (Main Endpoint)

#### `POST /query`

Processes a natural language query and returns SQL + results.

**Request:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user": "user_123",
    "nl": "¿Qué camión tuvo más alertas de temperatura en la última semana?"
  }'
```

**Request Body:**
```json
{
  "user": "string",      // User identifier (required)
  "nl": "string"         // Natural language query (required)
}
```

**Response (Success):**
```json
{
  "nl": "¿Qué camión tuvo más alertas de temperatura en la última semana?",
  "sql": "SELECT truck_id, COUNT(*) as alerts FROM alerts WHERE alert_type = 'temperature' AND timestamp >= datetime('now', '-7 days') GROUP BY truck_id ORDER BY alerts DESC LIMIT 5;",
  "rows": [
    {
      "truck_id": "TRUCK_042",
      "alerts": 15
    },
    {
      "truck_id": "TRUCK_023",
      "alerts": 12
    },
    {
      "truck_id": "TRUCK_007",
      "alerts": 9
    }
  ],
  "explanation": "El camión TRUCK_042 tuvo 15 alertas de temperatura en la última semana, seguido por TRUCK_023 con 12 alertas.",
  "execution_time_ms": 234.56,
  "rows_count": 3
}
```

**Response (Error - Invalid SQL):**
```json
{
  "detail": "SQL inválido: Token prohibido detectado: 'DROP'. No se permiten comandos DML/DDL."
}
```
Status Code: `400 Bad Request`

**Response (Error - Server):**
```json
{
  "detail": "Error procesando query: Database connection failed"
}
```
Status Code: `500 Internal Server Error`

---

### 5. Query Logs

#### `GET /logs`

Returns recent query logs.

**Request:**
```bash
curl http://localhost:8000/logs?limit=10
```

**Query Parameters:**
- `limit` (optional): Number of logs to return (default: 50)

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2025-10-21T13:15:30Z",
      "user": "user_123",
      "nl": "Lista de camiones en mantenimiento",
      "sql": "SELECT * FROM trucks WHERE status = 'maintenance' LIMIT 1000;",
      "exec_time_ms": 45.23,
      "rows_count": 5,
      "error": null
    },
    {
      "timestamp": "2025-10-21T13:14:22Z",
      "user": "user_456",
      "nl": "Alertas críticas",
      "sql": "SELECT * FROM alerts WHERE severity = 'critical' ORDER BY timestamp DESC LIMIT 10;",
      "exec_time_ms": 67.89,
      "rows_count": 10,
      "error": null
    }
  ]
}
```

---

## Example Queries

### Query 1: Temperature Alerts
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user": "demo",
    "nl": "¿Qué camión tuvo más alertas de temperatura en la última semana?"
  }'
```

### Query 2: Fuel Consumption
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user": "demo",
    "nl": "Promedio de consumo por marca de camión en los últimos 30 días"
  }'
```

### Query 3: Finished Trips
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user": "demo",
    "nl": "¿Cuántos viajes finalizados hubo ayer?"
  }'
```

### Query 4: Critical Alerts
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user": "demo",
    "nl": "Mostrar las 10 últimas alertas críticas"
  }'
```

### Query 5: Maintenance
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user": "demo",
    "nl": "Lista de camiones actualmente en mantenimiento"
  }'
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid SQL, validation error) |
| 500 | Internal Server Error |

---

## Rate Limiting

Currently not implemented in MVP. For production:
- Recommended: 100 requests/minute per user
- Implement using Redis + middleware

---

## Response Times

**Expected Performance:**
- Simple queries: < 500ms
- Queries with JOINs: < 1s
- Complex queries: < 2s
- SLA: < 5s (99th percentile)

---

## SQL Validation Rules

The API validates all generated SQL to ensure security:

### Allowed:
✅ `SELECT` statements  
✅ `WITH` clauses (CTEs)  
✅ `JOIN` operations  
✅ Aggregate functions (`COUNT`, `AVG`, `SUM`, etc.)  
✅ `WHERE`, `GROUP BY`, `ORDER BY`, `LIMIT`  

### Blocked:
❌ `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`  
❌ `EXEC`, `PRAGMA`, `ATTACH`, `DETACH`  
❌ Multiple statements (`;` in middle)  
❌ SQL comments (`--`, `/*`)  
❌ Queries without `LIMIT` (auto-added)  
❌ `LIMIT` > 10,000  

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Python Client Example

```python
import requests

# Configuration
API_URL = "http://localhost:8000"

# Make a query
response = requests.post(
    f"{API_URL}/query",
    json={
        "user": "my_user",
        "nl": "Lista de camiones en mantenimiento"
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"SQL: {data['sql']}")
    print(f"Results: {len(data['rows'])} rows")
    for row in data['rows']:
        print(row)
else:
    print(f"Error: {response.json()['detail']}")
```

---

## JavaScript Client Example

```javascript
// Configuration
const API_URL = 'http://localhost:8000';

// Make a query
async function queryLogiq(nlQuery) {
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user: 'my_user',
        nl: nlQuery
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('SQL:', data.sql);
      console.log('Results:', data.rows);
      return data;
    } else {
      const error = await response.json();
      console.error('Error:', error.detail);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}

// Usage
queryLogiq('Lista de camiones en mantenimiento');
```

---

## Webhooks (Future)

Not implemented in MVP. For production:

```json
{
  "webhook_url": "https://your-app.com/webhook",
  "events": ["query_completed", "query_failed"],
  "secret": "your_webhook_secret"
}
```

---

## Versioning

Current version: `v1.0.0`

Future versions will use URL versioning:
- `http://localhost:8000/v1/query`
- `http://localhost:8000/v2/query`

---

## Support

- 📖 Full Documentation: `README.md`
- 🚀 Quick Start: `QUICKSTART.md`
- 📋 Technical Summary: `SUMMARY.md`
- 📧 Email: logiq-ai@santex.com

---

**Last Updated**: 2025-10-21  
**API Version**: 1.0.0
