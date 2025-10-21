# 📚 LogiQ AI - Índice de Documentación

## 🎯 Guía Rápida por Rol

### 👨‍💼 Para Evaluadores / Jueces
1. **Empezar aquí**: [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) - Visión general del proyecto
2. **Demo rápida**: [`QUICKSTART.md`](QUICKSTART.md) - Ejecutar en 5 minutos
3. **Presentación**: [`slides/pitch.md`](slides/pitch.md) - Slides completos
4. **Arquitectura**: [`SUMMARY.md`](SUMMARY.md) - Detalles técnicos

### 👨‍💻 Para Desarrolladores
1. **Instalación**: [`INSTALLATION.md`](INSTALLATION.md) - Guía completa de setup
2. **API**: [`API.md`](API.md) - Documentación de endpoints
3. **Código**: Explorar `backend/`, `frontend/`, `adapters/`
4. **Tests**: `pytest tests/ -v`

### 🎤 Para Presentadores
1. **Script**: [`demo/demo_script.md`](demo/demo_script.md) - Guion de 2-3 minutos
2. **Slides**: [`slides/pitch.md`](slides/pitch.md) - Presentación completa
3. **Demo**: `./demo/run_demo.sh` - Ejecutar demo completo
4. **Queries**: Ver sección "10 Queries Demo" en [`SUMMARY.md`](SUMMARY.md)

### 👥 Para Usuarios Finales
1. **Inicio rápido**: [`QUICKSTART.md`](QUICKSTART.md)
2. **Manual**: [`README.md`](README.md)
3. **UI**: Abrir http://localhost:8501 después de ejecutar

---

## 📖 Documentación Completa

### 🚀 Getting Started

| Documento | Descripción | Tiempo | Audiencia |
|-----------|-------------|--------|-----------|
| [`QUICKSTART.md`](QUICKSTART.md) | Inicio rápido en 5 minutos | 5 min | Todos |
| [`INSTALLATION.md`](INSTALLATION.md) | Guía completa de instalación | 10 min | Desarrolladores |
| [`README.md`](README.md) | Documentación principal | 15 min | Todos |

### 📊 Visión General

| Documento | Descripción | Tiempo | Audiencia |
|-----------|-------------|--------|-----------|
| [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) | Overview ejecutivo completo | 10 min | Evaluadores, Inversores |
| [`SUMMARY.md`](SUMMARY.md) | Resumen técnico detallado | 15 min | Desarrolladores, Arquitectos |
| [`TODO.md`](TODO.md) | Roadmap y tareas pendientes | 5 min | Equipo de desarrollo |

### 🎯 Demo y Presentación

| Documento | Descripción | Tiempo | Audiencia |
|-----------|-------------|--------|-----------|
| [`demo/demo_script.md`](demo/demo_script.md) | Script de presentación | 2-3 min | Presentadores |
| [`slides/pitch.md`](slides/pitch.md) | Slides completos (10 slides) | 5-7 min | Presentadores, Evaluadores |

### 🔧 Técnico

| Documento | Descripción | Tiempo | Audiencia |
|-----------|-------------|--------|-----------|
| [`API.md`](API.md) | Documentación de API REST | 20 min | Desarrolladores |
| Código fuente | Ver estructura abajo | Variable | Desarrolladores |

### 📋 Otros

| Documento | Descripción | Audiencia |
|-----------|-------------|-----------|
| [`LICENSE`](LICENSE) | Licencia MIT | Todos |
| [`.env.example`](.env.example) | Template de configuración | Desarrolladores |
| [`requirements.txt`](requirements.txt) | Dependencias Python | Desarrolladores |
| [`Dockerfile`](Dockerfile) | Configuración Docker | DevOps |
| [`docker-compose.yml`](docker-compose.yml) | Orquestación Docker | DevOps |
| [`pytest.ini`](pytest.ini) | Configuración de tests | Desarrolladores |

---

## 🗂️ Estructura del Código

### Backend (`backend/`)

```
backend/
├── app.py                    # FastAPI application principal
│   ├── Endpoints: /, /health, /schema, /query, /logs
│   ├── Middleware: CORS
│   └── Logging y error handling
│
└── lib/
    ├── gemini_client.py      # Cliente Gemini AI (NL → SQL)
    │   ├── Modo API real
    │   ├── Modo mock (fallback)
    │   └── Few-shot prompting
    │
    └── validate_sql.py       # Validador de SQL
        ├── Whitelist de comandos
        ├── Validación de tablas
        ├── Auto-LIMIT
        └── Detección de SQL injection
```

**Archivos clave**:
- [`backend/app.py`](backend/app.py) - Aplicación principal
- [`backend/lib/gemini_client.py`](backend/lib/gemini_client.py) - NL → SQL
- [`backend/lib/validate_sql.py`](backend/lib/validate_sql.py) - Seguridad

### Frontend (`frontend/`)

```
frontend/
└── streamlit_app.py          # UI de chat
    ├── Interface conversacional
    ├── Botones de queries rápidas
    ├── Visualización de resultados
    ├── Descarga de CSV
    └── Gráficos básicos
```

**Archivo clave**:
- [`frontend/streamlit_app.py`](frontend/streamlit_app.py) - UI completa

### Adapters (`adapters/`)

```
adapters/
├── adapter_base.py           # Clase base abstracta
│   ├── DataAdapter (ABC)
│   ├── CSVAdapter
│   └── JSONAdapter
│
├── tera_adapter.py           # Adapter para Tera (viajes)
├── cloudfleet_adapter.py     # Adapter para Cloudfleet (telemetría)
├── scania_adapter.py         # Adapter para Scania (métricas)
└── keeper_adapter.py         # Adapter para Keeper (alertas)
```

**Archivos clave**:
- [`adapters/adapter_base.py`](adapters/adapter_base.py) - Clase base
- Adapters específicos para cada fuente

### Mappings (`mappings/`)

```
mappings/
├── tera_mapping.yaml         # Mapeo Tera → Schema canónico
├── cloudfleet_mapping.yaml   # Mapeo Cloudfleet → Schema canónico
├── scania_mapping.yaml       # Mapeo Scania → Schema canónico
└── keeper_mapping.yaml       # Mapeo Keeper → Schema canónico
```

**Formato**: YAML con mapeo campo_destino: campo_origen

### Scripts (`scripts/`)

```
scripts/
├── generate_data.py          # Genera CSVs simulados
│   ├── 50 camiones
│   ├── 60 conductores
│   ├── 500 viajes
│   ├── 2000 telemetría
│   └── 300 alertas
│
└── load_data.py              # Carga datos en SQLite
    ├── Crea schema canónico
    ├── Ejecuta adapters
    └── Inserta en DB
```

**Archivos clave**:
- [`scripts/generate_data.py`](scripts/generate_data.py) - Generación de datos
- [`scripts/load_data.py`](scripts/load_data.py) - ETL

### Tests (`tests/`)

```
tests/
├── test_adapters.py          # Tests unitarios de adapters
├── test_sql_validator.py     # Tests del validador SQL
└── test_end_to_end.py        # Tests E2E del flujo completo
```

**Ejecutar**: `pytest tests/ -v`

### Demo (`demo/`)

```
demo/
├── run_demo.sh               # Script de demo completo
└── demo_script.md            # Guion de presentación
```

### Slides (`slides/`)

```
slides/
└── pitch.md                  # Presentación completa (10 slides)
```

---

## 🎯 Flujos de Trabajo Comunes

### 1. Primera Instalación

```bash
# 1. Setup
./setup.sh

# 2. Verificar
./verify_setup.sh

# 3. Iniciar backend
./run_backend.sh

# 4. Iniciar frontend (nueva terminal)
./run_frontend.sh
```

**Documentación**: [`INSTALLATION.md`](INSTALLATION.md)

---

### 2. Desarrollo

```bash
# 1. Activar entorno
source venv/bin/activate

# 2. Hacer cambios en código

# 3. Ejecutar tests
pytest tests/ -v

# 4. Reiniciar backend (auto-reload habilitado)
# Los cambios se reflejan automáticamente
```

**Documentación**: [`README.md`](README.md), código fuente

---

### 3. Agregar Nuevos Datos

```bash
# 1. Editar scripts/generate_data.py
# 2. Regenerar datos
python3 scripts/generate_data.py

# 3. Recargar en DB
rm data/logiq.db
python3 scripts/load_data.py

# 4. Reiniciar backend
```

**Documentación**: [`scripts/generate_data.py`](scripts/generate_data.py)

---

### 4. Agregar Nueva Fuente de Datos

```bash
# 1. Crear mapping YAML
# mappings/nueva_fuente_mapping.yaml

# 2. Crear adapter
# adapters/nueva_fuente_adapter.py

# 3. Actualizar load_data.py

# 4. Regenerar datos
```

**Documentación**: [`adapters/adapter_base.py`](adapters/adapter_base.py)

---

### 5. Preparar Demo

```bash
# 1. Leer script
cat demo/demo_script.md

# 2. Revisar slides
cat slides/pitch.md

# 3. Ejecutar demo completo
./demo/run_demo.sh

# 4. Practicar queries de ejemplo
```

**Documentación**: [`demo/demo_script.md`](demo/demo_script.md)

---

## 🔍 Búsqueda Rápida

### ¿Cómo hacer X?

| Tarea | Documento | Sección |
|-------|-----------|---------|
| Instalar el proyecto | [`INSTALLATION.md`](INSTALLATION.md) | Instalación Paso a Paso |
| Ejecutar tests | [`INSTALLATION.md`](INSTALLATION.md) | Ejecutar Tests |
| Agregar API key | [`INSTALLATION.md`](INSTALLATION.md) | Configurar API Key |
| Ver ejemplos de queries | [`SUMMARY.md`](SUMMARY.md) | 10 Queries Demo |
| Entender arquitectura | [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) | Arquitectura Técnica |
| Usar la API | [`API.md`](API.md) | Endpoints |
| Preparar presentación | [`demo/demo_script.md`](demo/demo_script.md) | Todo el documento |
| Troubleshooting | [`INSTALLATION.md`](INSTALLATION.md) | Solución de Problemas |

---

## 📞 Contacto y Soporte

### Documentación
- **Completa**: Este índice + documentos enlazados
- **Rápida**: [`QUICKSTART.md`](QUICKSTART.md)
- **Técnica**: [`API.md`](API.md), [`SUMMARY.md`](SUMMARY.md)

### Soporte
- 📧 Email: logiq-ai@santex.com
- 🌐 Web: logiq-ai.demo
- 💼 LinkedIn: /logiq-ai

### Contribuir
- Ver [`TODO.md`](TODO.md) para tareas pendientes
- Fork + Pull Request
- Seguir guidelines en código

---

## 📊 Estadísticas del Proyecto

### Código
- **Líneas de código**: ~3,000
- **Archivos Python**: 15+
- **Tests**: 20+
- **Cobertura**: 80%+

### Documentación
- **Páginas**: 10+ documentos
- **Palabras**: 20,000+
- **Ejemplos**: 50+
- **Diagramas**: 5+

### Datos
- **Tablas**: 5
- **Registros**: 2,900+
- **Fuentes**: 4
- **Queries demo**: 10

---

## ✅ Checklist de Verificación

Antes de demo/presentación:

- [ ] Leído [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md)
- [ ] Ejecutado `./verify_setup.sh` exitosamente
- [ ] Backend responde en http://localhost:8000/health
- [ ] Frontend carga en http://localhost:8501
- [ ] Probado al menos 3 queries de ejemplo
- [ ] Tests pasan (`pytest tests/ -v`)
- [ ] Revisado [`demo/demo_script.md`](demo/demo_script.md)
- [ ] Slides listos ([`slides/pitch.md`](slides/pitch.md))

---

## 🎓 Recursos de Aprendizaje

### Para entender el proyecto:
1. [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) - Visión general
2. [`SUMMARY.md`](SUMMARY.md) - Detalles técnicos
3. Código fuente con comentarios

### Para usar el proyecto:
1. [`QUICKSTART.md`](QUICKSTART.md) - Inicio rápido
2. [`README.md`](README.md) - Manual completo
3. [`API.md`](API.md) - Referencia de API

### Para presentar el proyecto:
1. [`demo/demo_script.md`](demo/demo_script.md) - Guion
2. [`slides/pitch.md`](slides/pitch.md) - Slides
3. Práctica con queries reales

---

## 🚀 Próximos Pasos

Después de revisar este índice:

1. **Evaluadores**: Leer [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md)
2. **Desarrolladores**: Seguir [`INSTALLATION.md`](INSTALLATION.md)
3. **Presentadores**: Revisar [`demo/demo_script.md`](demo/demo_script.md)
4. **Usuarios**: Ejecutar [`QUICKSTART.md`](QUICKSTART.md)

---

**Última actualización**: 2025-10-21  
**Versión**: 1.0.0 (MVP)  
**Status**: ✅ Completo y listo para demo

---

**¡Bienvenido a LogiQ AI! 🚛🚀**
