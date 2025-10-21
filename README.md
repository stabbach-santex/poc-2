# 🚛 LogiQ AI - Asistente Conversacional para Data Warehouse Logístico

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Consulta tu data warehouse logístico en lenguaje natural. Integra 4 fuentes de datos (Tera, Cloudfleet, Scania, Keeper) y genera SQL seguro con IA.

---

## ⚡ Quick Start (5 minutos)

### Requisitos
- Python 3.10+
- pip

### Instalación y Ejecución (3 comandos)

```bash
# 1. Setup: instalar dependencias y crear entorno
./setup.sh

# 2. Backend: cargar datos y levantar API
./run_backend.sh

# 3. Frontend: abrir UI de chat (en otra terminal)
./run_frontend.sh
```

**URLs**:
- 🎨 Frontend: http://localhost:8501
- 📡 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

### Demo Completo
```bash
./demo/run_demo.sh
```

---

## 📚 Documentación Completa

| Documento | Descripción | Para quién |
|-----------|-------------|------------|
| **[INDEX.md](INDEX.md)** | 📖 Índice navegable de toda la documentación | Todos |
| **[QUICKSTART.md](QUICKSTART.md)** | ⚡ Inicio rápido en 5 minutos | Nuevos usuarios |
| **[INSTALLATION.md](INSTALLATION.md)** | 🔧 Guía completa de instalación | Desarrolladores |
| **[API.md](API.md)** | 📡 Documentación de API REST | Desarrolladores |
| **[SUMMARY.md](SUMMARY.md)** | 📋 Resumen técnico detallado | Técnicos |
| **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** | 🎯 Overview ejecutivo | Evaluadores |
| **[TODO.md](TODO.md)** | 📝 Roadmap y tareas | Equipo |
| **[demo/demo_script.md](demo/demo_script.md)** | 🎤 Script de presentación | Presentadores |
| **[slides/pitch.md](slides/pitch.md)** | 📊 Slides completos | Presentadores |

**👉 Empezar por**: [`INDEX.md`](INDEX.md) para navegación completa

## 📁 Estructura del Proyecto

```
logiq-ai-proto/
├── data/                    # Datasets simulados (CSVs)
├── adapters/                # Transformadores de datos
├── mappings/                # Configuraciones YAML de mapeo
├── backend/                 # FastAPI application
│   └── lib/                 # Librerías (Gemini, validator)
├── frontend/                # Streamlit UI
├── tests/                   # Tests automatizados
├── demo/                    # Assets de demostración
├── slides/                  # Presentación
├── scripts/                 # Scripts de utilidad
└── logs/                    # Query logs
```

## 🔧 Variables de Entorno

Crear archivo `.env` en la raíz:

```bash
# API Keys (al menos una requerida)
GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_key_here  # alternativa

# BigQuery (opcional)
USE_BIGQUERY=false
# BQ_PROJECT=your-gcp-project
# BQ_DATASET=logiq_warehouse

# Configuración
PORT=8000
```

## 📊 Schema Canónico

El data warehouse normalizado contiene 5 tablas:

1. **trucks**: Información de camiones
2. **drivers**: Datos de conductores
3. **trips**: Viajes realizados
4. **telemetry**: Telemetría en tiempo real
5. **alerts**: Alertas y eventos

## 🧪 Tests

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/test_adapters.py
pytest tests/test_sql_validator.py
pytest tests/test_end_to_end.py
```

## 📡 API Endpoints

### POST /query
Procesa consulta en lenguaje natural y retorna SQL + resultados.

**Request:**
```json
{
  "user": "user_123",
  "nl": "¿Qué camión tuvo más alertas en la última semana?"
}
```

**Response:**
```json
{
  "nl": "¿Qué camión tuvo más alertas en la última semana?",
  "sql": "SELECT truck_id, COUNT(*) as alerts FROM alerts...",
  "rows": [...],
  "explanation": "El camión T042 tuvo 15 alertas...",
  "execution_time_ms": 234
}
```

## 🎯 Queries Demo

1. "¿Qué camión tuvo más alertas de temperatura en la última semana?"
2. "Promedio de consumo por marca de camión en los últimos 30 días"
3. "¿Cuántos viajes finalizados hubo ayer?"
4. "Mostrar las 10 últimas alertas críticas"
5. "Lista de camiones actualmente en mantenimiento"
6. "Top 5 rutas con más retrasos"
7. "¿Cuál es el conductor con más kilómetros recorridos este mes?"
8. "Alertas de velocidad excesiva en la última semana"
9. "Camiones con nivel de combustible bajo (< 20%)"
10. "Viajes más largos por región"

## 🏗️ Arquitectura

```
Usuario → Streamlit UI → FastAPI Backend → Gemini API
                              ↓
                         SQL Validator
                              ↓
                      SQLite/BigQuery
```

## 🔒 Seguridad

- **SQL Validator**: Solo permite SELECT y WITH
- **Whitelist**: Tablas y columnas validadas contra schema
- **Auto-LIMIT**: Máximo 1000 filas por query
- **Banned tokens**: Previene DML/DDL (DROP, DELETE, etc.)

## 📝 Logs

Los queries se registran en `logs/queries.log`:
```
timestamp | user | nl_query | generated_sql | exec_time_ms | rows_count
```

## 🐳 Docker (Opcional)

```bash
docker-compose up
```

## 🤝 Contribuir

Este es un prototipo MVP para hackathon. Para producción considerar:
- Autenticación y autorización
- Rate limiting
- Caché de queries
- Monitoreo y alertas
- Escalabilidad horizontal

## 📄 Licencia

MIT License - Ver LICENSE file

## 👥 Equipo

Desarrollado para GLAC Hackathon 2025
