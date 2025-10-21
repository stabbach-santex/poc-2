# 🚀 LogiQ AI - Quick Start Guide

## ⚡ Inicio Rápido (5 minutos)

### Paso 1: Instalación

```bash
# Clonar o navegar al directorio del proyecto
cd /Users/santitabbach/Documents/Work/Santex/GLAC/Hackathon/poc-2

# Ejecutar setup (instala dependencias y crea estructura)
./setup.sh
```

**Nota**: El setup creará un archivo `.env` template. Puedes usar el sistema sin configurar API keys (modo mock).

---

### Paso 2: Configurar API Key (Opcional)

Para usar Gemini AI real (recomendado para producción):

```bash
# Editar .env
nano .env

# Agregar tu API key:
GEMINI_API_KEY=tu_api_key_aqui
```

**Obtener API Key**: https://makersuite.google.com/app/apikey

**Sin API Key**: El sistema funciona en modo mock con templates predefinidos.

---

### Paso 3: Iniciar Backend

```bash
# Terminal 1: Backend
./run_backend.sh
```

Esto hará:
1. ✅ Generar datos simulados (si no existen)
2. ✅ Cargar datos en SQLite
3. ✅ Iniciar API en http://localhost:8000

**Verificar**: Abrir http://localhost:8000/health en el navegador

---

### Paso 4: Iniciar Frontend

```bash
# Terminal 2: Frontend (nueva terminal)
./run_frontend.sh
```

Esto abrirá automáticamente http://localhost:8501 en tu navegador.

---

### Paso 5: ¡Probar!

En la UI de Streamlit, prueba estas consultas:

1. **"¿Qué camión tuvo más alertas de temperatura en la última semana?"**
2. **"Promedio de consumo por marca de camión"**
3. **"Lista de camiones en mantenimiento"**

---

## 🎯 Demo Completo (Alternativa)

Para iniciar todo de una vez:

```bash
./demo/run_demo.sh
```

Este script:
- ✅ Verifica dependencias
- ✅ Genera y carga datos
- ✅ Inicia backend y frontend
- ✅ Muestra comandos de ejemplo

---

## 🧪 Ejecutar Tests

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/test_adapters.py -v
pytest tests/test_sql_validator.py -v

# Tests e2e (requiere backend corriendo)
pytest tests/test_end_to_end.py -v
```

---

## 📡 Probar la API con cURL

```bash
# Health check
curl http://localhost:8000/health

# Schema
curl http://localhost:8000/schema

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "nl": "Lista de camiones en mantenimiento"
  }'

# Ver logs
curl http://localhost:8000/logs?limit=5
```

---

## 🔧 Troubleshooting

### Error: "Base de datos no encontrada"

```bash
# Generar datos manualmente
source venv/bin/activate
python3 scripts/generate_data.py
python3 scripts/load_data.py
```

---

### Error: "No se puede conectar al backend"

```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/health

# Si no responde, reiniciar:
./run_backend.sh
```

---

### Error: "ModuleNotFoundError"

```bash
# Reinstalar dependencias
source venv/bin/activate
pip install -r requirements.txt
```

---

### Puerto 8000 o 8501 ya en uso

```bash
# Encontrar y matar proceso
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9

# O cambiar puerto en .env
echo "PORT=8001" >> .env
```

---

## 📊 Estructura del Proyecto

```
logiq-ai-proto/
├── setup.sh              ← Ejecutar primero
├── run_backend.sh        ← Iniciar API
├── run_frontend.sh       ← Iniciar UI
├── demo/run_demo.sh      ← Demo completo
│
├── data/                 ← Datos y DB
│   ├── *.csv            (generados automáticamente)
│   └── logiq.db         (SQLite database)
│
├── backend/              ← FastAPI
│   ├── app.py           (aplicación principal)
│   └── lib/             (validador, Gemini client)
│
├── frontend/             ← Streamlit
│   └── streamlit_app.py
│
├── adapters/             ← Transformadores de datos
├── mappings/             ← Configuraciones YAML
├── scripts/              ← Utilidades
├── tests/                ← Tests automatizados
└── demo/                 ← Assets de demostración
```

---

## 🎓 Próximos Pasos

### Para Desarrolladores

1. **Explorar el código**:
   - `backend/app.py` - Endpoint principal
   - `backend/lib/gemini_client.py` - NL → SQL
   - `backend/lib/validate_sql.py` - Validador

2. **Agregar más queries**:
   - Editar `SYSTEM_PROMPT` en `gemini_client.py`
   - Agregar ejemplos few-shot

3. **Personalizar datos**:
   - Editar `scripts/generate_data.py`
   - Aumentar número de registros

### Para Presentadores

1. **Leer el script de demo**: `demo/demo_script.md`
2. **Revisar slides**: `slides/pitch.md`
3. **Practicar con queries de ejemplo**

### Para Evaluadores

1. **Ver documentación completa**: `README.md`
2. **Revisar arquitectura**: `SUMMARY.md`
3. **Ejecutar tests**: `pytest tests/ -v`

---

## 📞 Soporte

- 📖 **Documentación completa**: `README.md`
- 📋 **Resumen técnico**: `SUMMARY.md`
- 📝 **TODOs y roadmap**: `TODO.md`
- 🎬 **Script de demo**: `demo/demo_script.md`
- 📊 **Presentación**: `slides/pitch.md`

---

## ✅ Checklist de Verificación

Antes de la demo, verificar:

- [ ] Backend responde en http://localhost:8000/health
- [ ] Frontend carga en http://localhost:8501
- [ ] Base de datos tiene datos (ver logs de carga)
- [ ] Al menos 3 queries de ejemplo funcionan
- [ ] Tests pasan (`pytest tests/ -v`)

---

## 🎉 ¡Listo!

Tu sistema LogiQ AI está funcionando. Ahora puedes:

- 💬 Hacer consultas en lenguaje natural
- 📊 Ver resultados en tiempo real
- 🔍 Inspeccionar el SQL generado
- 📥 Descargar resultados en CSV
- 📈 Visualizar datos en gráficos

**¡Disfruta explorando tus datos logísticos! 🚛**

---

**Tiempo total de setup**: ~5 minutos  
**Requisitos**: Python 3.10+, pip  
**Plataformas**: macOS, Linux, Windows (WSL)
