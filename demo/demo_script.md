# 🚛 LogiQ AI - Script de Demostración

## Duración: 2-3 minutos

---

## 🎯 Introducción (30 segundos)

**"Buenos días/tardes. Les presento LogiQ AI."**

### El Problema
Las empresas logísticas manejan datos de múltiples fuentes:
- **Tera**: Datos de viajes
- **Cloudfleet**: Telemetría GPS
- **Scania**: Métricas de vehículos
- **Keeper**: Sistema de alertas

Cada fuente tiene su propio formato, API y estructura. Los analistas necesitan conocimientos técnicos de SQL para extraer insights.

### La Solución
**LogiQ AI**: Un asistente conversacional que permite consultar todo el data warehouse en lenguaje natural.

---

## 🏗️ Arquitectura (30 segundos)

**[Mostrar slide de arquitectura]**

### Componentes:
1. **Adapters**: Normalizan datos de 4 fuentes diferentes
2. **Data Warehouse**: Schema canónico en SQLite/BigQuery
3. **Gemini AI**: Convierte lenguaje natural a SQL
4. **Validador SQL**: Previene queries peligrosas
5. **API FastAPI**: Backend robusto y escalable
6. **UI Streamlit**: Interfaz intuitiva de chat

### Flujo:
```
Usuario → "¿Qué camión tuvo más alertas?"
       ↓
    Gemini AI (NL → SQL)
       ↓
    Validador SQL (seguridad)
       ↓
    SQLite/BigQuery (ejecución)
       ↓
    Resultados + Explicación
```

---

## 💻 Demo en Vivo (60-90 segundos)

### Query 1: Alertas Críticas
**Pregunta**: *"Mostrar las 10 últimas alertas críticas"*

**Mostrar**:
- ✅ SQL generado automáticamente
- ✅ Resultados en tabla
- ✅ Tiempo de respuesta (< 1 segundo)
- ✅ Explicación en lenguaje natural

**Insight**: "Vemos que el camión TRUCK_042 tiene múltiples alertas de temperatura..."

---

### Query 2: Análisis de Consumo
**Pregunta**: *"Promedio de consumo por marca de camión en los últimos 30 días"*

**Mostrar**:
- ✅ JOIN automático entre tablas (trucks + telemetry)
- ✅ Agregación (AVG, GROUP BY)
- ✅ Filtro temporal (últimos 30 días)
- ✅ Visualización en gráfico

**Insight**: "Scania tiene el mejor promedio de eficiencia de combustible..."

---

### Query 3: Operaciones en Tiempo Real
**Pregunta**: *"¿Cuántos camiones están actualmente en mantenimiento?"*

**Mostrar**:
- ✅ Query simple pero efectiva
- ✅ Respuesta instantánea
- ✅ Datos actualizados

**Insight**: "5 camiones en mantenimiento - podemos ver sus detalles..."

---

## 🔒 Seguridad (20 segundos)

**Demostrar validador SQL**:

**Intento malicioso**: *"DROP TABLE trucks"*

**Resultado**: 
- ❌ Query rechazada
- ✅ Validador previene DML/DDL
- ✅ Solo permite SELECT
- ✅ Auto-LIMIT para prevenir sobrecarga

---

## 📊 Valor de Negocio (20 segundos)

### Beneficios Inmediatos:
1. **Democratización de datos**: Cualquier usuario puede consultar sin SQL
2. **Tiempo de respuesta**: De horas a segundos
3. **Reducción de errores**: SQL validado y seguro
4. **Escalabilidad**: Arquitectura lista para producción
5. **Multi-fuente**: Integra 4 sistemas diferentes

### ROI Estimado:
- ⏱️ **80% reducción** en tiempo de análisis
- 👥 **5x más usuarios** pueden acceder a datos
- 🔒 **100% queries seguros** (validación automática)

---

## 🚀 Próximos Pasos (10 segundos)

### Roadmap:
1. ✅ **MVP funcional** (completado)
2. 🔄 **Integración con APIs reales** (2 semanas)
3. 📈 **Dashboard de KPIs** (1 mes)
4. 🤖 **Alertas proactivas** (2 meses)
5. 🌐 **Multi-tenant SaaS** (3 meses)

---

## 🎬 Cierre (10 segundos)

**"LogiQ AI transforma cómo las empresas logísticas acceden a sus datos."**

**"De SQL complejo a conversación natural."**

**"¿Preguntas?"**

---

## 📝 Notas para el Presentador

### Tips:
- Mantener energía alta
- Mostrar queries reales, no slides
- Enfatizar la velocidad de respuesta
- Destacar la seguridad (validador SQL)
- Preparar 2-3 queries de backup por si algo falla

### Queries de Backup:
1. "Lista de conductores con más kilómetros"
2. "Alertas de velocidad excesiva"
3. "Viajes más largos por región"

### Posibles Preguntas:
**P: ¿Funciona con otros idiomas?**
R: Sí, Gemini soporta múltiples idiomas. Actualmente optimizado para español.

**P: ¿Qué pasa si Gemini genera SQL incorrecto?**
R: El validador SQL previene queries peligrosas. Si el SQL es sintácticamente incorrecto, retornamos error y el usuario puede reformular.

**P: ¿Cuánto cuesta?**
R: Gemini API: ~$0.001 por query. Infraestructura: ~$50/mes para 10K queries/día.

**P: ¿Tiempo de implementación?**
R: MVP en 2 semanas. Producción completa en 2-3 meses.

---

## 🎯 Métricas de Éxito del Demo

- ✅ Demostrar 3 queries diferentes
- ✅ Tiempo de respuesta < 2 segundos
- ✅ Mostrar validación de seguridad
- ✅ Explicar arquitectura claramente
- ✅ Generar interés/preguntas de la audiencia

---

**¡Éxito en tu presentación! 🚀**
