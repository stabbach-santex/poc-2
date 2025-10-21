# 🔧 LogiQ AI - Guía de Instalación Completa

## 📋 Requisitos Previos

### Sistema Operativo
- macOS 10.15+
- Linux (Ubuntu 20.04+, Debian 10+)
- Windows 10+ (con WSL2)

### Software Requerido
- **Python 3.10+** (verificar: `python3 --version`)
- **pip** (verificar: `python3 -m pip --version`)
- **Git** (opcional, para clonar)

---

## 🚀 Instalación Paso a Paso

### Opción 1: Instalación Automática (Recomendada)

```bash
# 1. Navegar al directorio del proyecto
cd /Users/santitabbach/Documents/Work/Santex/GLAC/Hackathon/poc-2

# 2. Ejecutar script de setup
./setup.sh

# 3. Activar entorno virtual
source venv/bin/activate

# 4. Verificar instalación
./verify_setup.sh
```

---

### Opción 2: Instalación Manual

#### Paso 1: Crear Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # macOS/Linux
# o
venv\Scripts\activate  # Windows
```

#### Paso 2: Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

#### Paso 3: Crear Directorios

```bash
mkdir -p data adapters mappings backend/lib frontend tests demo slides scripts logs
```

#### Paso 4: Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar .env (opcional - funciona sin API key en modo mock)
nano .env
```

---

## ⚙️ Configuración

### Configurar API Key de Gemini (Opcional)

1. **Obtener API Key**:
   - Visitar: https://makersuite.google.com/app/apikey
   - Crear una API key
   - Copiar la key

2. **Configurar en .env**:
   ```bash
   # Editar archivo .env
   nano .env
   
   # Agregar tu API key:
   GEMINI_API_KEY=tu_api_key_aqui
   ```

3. **Sin API Key**:
   - El sistema funciona en modo mock
   - Usa templates predefinidos
   - Perfecto para desarrollo y demos

---

## 🗄️ Preparar Base de Datos

### Generar Datos Simulados

```bash
# Activar entorno virtual (si no está activado)
source venv/bin/activate

# Generar CSVs simulados
python3 scripts/generate_data.py

# Cargar datos en SQLite
python3 scripts/load_data.py
```

**Resultado esperado**:
- `data/logiq.db` creado
- 50 camiones
- 60 conductores
- 500 viajes
- 2000 registros de telemetría
- 300 alertas

---

## ✅ Verificación de Instalación

### Ejecutar Script de Verificación

```bash
./verify_setup.sh
```

**Resultado esperado**:
```
✅ TODO PERFECTO!
```

### Verificación Manual

```bash
# 1. Verificar Python
python3 --version
# Debe mostrar: Python 3.10.x o superior

# 2. Verificar entorno virtual
which python
# Debe mostrar: .../venv/bin/python

# 3. Verificar dependencias
pip list | grep fastapi
pip list | grep streamlit

# 4. Verificar base de datos
ls -lh data/logiq.db
# Debe existir y tener ~50KB+

# 5. Verificar estructura
tree -L 2
```

---

## 🚀 Iniciar la Aplicación

### Método 1: Scripts Separados (Recomendado para Desarrollo)

**Terminal 1 - Backend:**
```bash
./run_backend.sh
```
Esperar mensaje: `✅ Backend corriendo en http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
./run_frontend.sh
```
Esperar mensaje: `You can now view your Streamlit app in your browser.`

### Método 2: Demo Completo (Recomendado para Presentaciones)

```bash
./demo/run_demo.sh
```

Este script:
- Verifica dependencias
- Genera datos (si no existen)
- Inicia backend y frontend
- Muestra comandos de ejemplo

### Método 3: Docker (Opcional)

```bash
# Construir y ejecutar
docker-compose up --build

# Acceder:
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

---

## 🧪 Ejecutar Tests

### Todos los Tests

```bash
source venv/bin/activate
pytest tests/ -v
```

### Tests Específicos

```bash
# Tests de adapters
pytest tests/test_adapters.py -v

# Tests de validador SQL
pytest tests/test_sql_validator.py -v

# Tests end-to-end (requiere backend corriendo)
pytest tests/test_end_to_end.py -v
```

---

## 🔍 Verificar que Todo Funciona

### 1. Backend API

```bash
# Health check
curl http://localhost:8000/health

# Debe retornar:
# {"status":"healthy","database":"connected","trucks_count":50}
```

### 2. Query de Prueba

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test",
    "nl": "Lista de camiones"
  }'
```

### 3. Frontend UI

Abrir en navegador: http://localhost:8501

Probar query: "Lista de camiones en mantenimiento"

---

## 🐛 Solución de Problemas

### Error: "python3: command not found"

**Solución**:
```bash
# macOS
brew install python@3.10

# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv

# Verificar
python3 --version
```

---

### Error: "pip: command not found"

**Solución**:
```bash
# Instalar pip
python3 -m ensurepip --upgrade

# o
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

---

### Error: "Permission denied" al ejecutar scripts

**Solución**:
```bash
chmod +x setup.sh run_backend.sh run_frontend.sh demo/run_demo.sh verify_setup.sh
```

---

### Error: "Port 8000 already in use"

**Solución**:
```bash
# Encontrar proceso usando el puerto
lsof -ti:8000

# Matar proceso
lsof -ti:8000 | xargs kill -9

# O cambiar puerto en .env
echo "PORT=8001" >> .env
```

---

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Solución**:
```bash
# Verificar que el entorno virtual está activado
source venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

---

### Error: "Database not found"

**Solución**:
```bash
# Generar datos
python3 scripts/generate_data.py
python3 scripts/load_data.py

# Verificar
ls -lh data/logiq.db
```

---

### Error: "Streamlit not found"

**Solución**:
```bash
source venv/bin/activate
pip install streamlit
```

---

### Frontend no conecta con Backend

**Solución**:
```bash
# 1. Verificar que backend está corriendo
curl http://localhost:8000/health

# 2. Si no responde, reiniciar backend
./run_backend.sh

# 3. Verificar firewall/antivirus no bloquea puerto 8000
```

---

## 🔄 Actualización

### Actualizar Dependencias

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Regenerar Datos

```bash
# Eliminar base de datos antigua
rm data/logiq.db

# Regenerar
python3 scripts/generate_data.py
python3 scripts/load_data.py
```

---

## 🗑️ Desinstalación

### Eliminar Entorno Virtual

```bash
deactivate  # Si está activado
rm -rf venv
```

### Eliminar Datos

```bash
rm -rf data/*.csv data/*.db
rm -rf logs/*.log
```

### Eliminar Todo

```bash
cd ..
rm -rf logiq-ai-proto
```

---

## 📦 Instalación en Diferentes Sistemas

### macOS

```bash
# Instalar Homebrew (si no está instalado)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python
brew install python@3.10

# Continuar con instalación normal
./setup.sh
```

### Ubuntu/Debian

```bash
# Actualizar sistema
sudo apt update
sudo apt upgrade

# Instalar Python y dependencias
sudo apt install python3.10 python3.10-venv python3-pip

# Continuar con instalación normal
./setup.sh
```

### Windows (WSL2)

```bash
# 1. Instalar WSL2
wsl --install

# 2. Instalar Ubuntu desde Microsoft Store

# 3. Dentro de WSL, seguir pasos de Ubuntu
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# 4. Continuar con instalación normal
./setup.sh
```

---

## 🐳 Instalación con Docker

### Requisitos
- Docker Desktop instalado
- Docker Compose instalado

### Instalación

```bash
# 1. Construir imagen
docker-compose build

# 2. Iniciar servicios
docker-compose up

# 3. Acceder
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

### Comandos Útiles

```bash
# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reiniciar
docker-compose restart

# Eliminar todo
docker-compose down -v
```

---

## 📊 Verificación Post-Instalación

### Checklist

- [ ] Python 3.10+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Directorios creados
- [ ] Datos generados y cargados
- [ ] Backend responde en http://localhost:8000/health
- [ ] Frontend carga en http://localhost:8501
- [ ] Tests pasan (`pytest tests/ -v`)
- [ ] Query de prueba funciona

---

## 🎓 Próximos Pasos

Después de la instalación exitosa:

1. **Leer documentación**: `README.md`, `QUICKSTART.md`
2. **Probar queries**: Ver `SUMMARY.md` para ejemplos
3. **Revisar código**: Explorar `backend/` y `frontend/`
4. **Ejecutar demo**: `./demo/run_demo.sh`
5. **Personalizar**: Editar datos, queries, UI

---

## 📞 Soporte

Si encuentras problemas:

1. **Verificar setup**: `./verify_setup.sh`
2. **Revisar logs**: `logs/backend.log`, `logs/queries.log`
3. **Consultar docs**: `README.md`, `TROUBLESHOOTING.md`
4. **Contactar**: logiq-ai@santex.com

---

## ✅ Instalación Exitosa

Si llegaste hasta aquí y todo funciona:

🎉 **¡Felicitaciones!** LogiQ AI está instalado y listo para usar.

Próximos comandos:
```bash
# Terminal 1
./run_backend.sh

# Terminal 2
./run_frontend.sh

# Abrir: http://localhost:8501
```

---

**Tiempo estimado de instalación**: 5-10 minutos  
**Dificultad**: Fácil  
**Soporte**: ✅ Disponible
