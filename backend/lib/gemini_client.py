"""
Cliente para interactuar con Gemini API y generar SQL desde lenguaje natural.
Incluye fallback a templates si la API no está disponible.
"""

import os
import re
from typing import Optional, Dict


# Prompt system con schema y ejemplos (few-shot learning)
SYSTEM_PROMPT = """Eres un asistente experto que genera SQL seguro para una base de datos SQLite con las siguientes tablas y columnas:

SCHEMA CANÓNICO:
- trucks(truck_id TEXT, plate TEXT, model TEXT, brand TEXT, driver_id TEXT, region TEXT, status TEXT)
- drivers(driver_id TEXT, name TEXT, license TEXT)
- trips(trip_id TEXT, truck_id TEXT, origin TEXT, destination TEXT, start_time TEXT, end_time TEXT, distance_km REAL, status TEXT)
- telemetry(telemetry_id TEXT, truck_id TEXT, timestamp TEXT, speed_kmh REAL, fuel_level REAL, engine_temp_c REAL)
- alerts(alert_id TEXT, truck_id TEXT, timestamp TEXT, alert_type TEXT, severity TEXT, description TEXT)

INSTRUCCIONES:
- SOLO genera una consulta SELECT válida en SQL compatible con SQLite.
- No incluyas comandos DDL/DML (CREATE, DROP, DELETE, UPDATE, INSERT, ALTER).
- Añade siempre LIMIT si no está presente (máximo 1000).
- Usa funciones de fecha de SQLite: date(), datetime(), time().
- Para fechas relativas usa: datetime('now', '-N days/hours').
- No expliques nada en la salida; retorna SOLO el SQL.
- El SQL debe terminar con punto y coma (;).

EJEMPLOS (few-shot):

1. NL: "¿Qué camión tuvo más alertas de temperatura en la última semana?"
SQL: SELECT truck_id, COUNT(*) as alerts FROM alerts WHERE alert_type = 'temperature' AND timestamp >= datetime('now', '-7 days') GROUP BY truck_id ORDER BY alerts DESC LIMIT 5;

2. NL: "Promedio de consumo por marca de camión en los últimos 30 días"
SQL: SELECT t.brand, AVG(tele.fuel_level) as avg_fuel_level FROM trucks t JOIN telemetry tele ON t.truck_id = tele.truck_id WHERE tele.timestamp >= datetime('now','-30 days') GROUP BY t.brand;

3. NL: "¿Cuántos viajes finalizados hubo ayer?"
SQL: SELECT COUNT(*) as trips_finished FROM trips WHERE status = 'finished' AND date(end_time) = date('now','-1 day');

4. NL: "Mostrar las 10 últimas alertas críticas"
SQL: SELECT * FROM alerts WHERE severity = 'critical' ORDER BY timestamp DESC LIMIT 10;

5. NL: "Lista de camiones actualmente en mantenimiento"
SQL: SELECT * FROM trucks WHERE status = 'maintenance';

6. NL: "Top 5 rutas con más retrasos"
SQL: WITH trip_delays AS (SELECT trip_id, origin, destination, (julianday(end_time) - julianday(start_time)) * 24 as duration_hours FROM trips WHERE status = 'finished') SELECT origin, destination, AVG(duration_hours) as avg_duration FROM trip_delays GROUP BY origin, destination ORDER BY avg_duration DESC LIMIT 5;

Ahora genera SQL para la siguiente pregunta:
"""


class GeminiClient:
    """Cliente para generar SQL usando Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el cliente Gemini.
        
        Args:
            api_key: API key de Gemini (si no se provee, usa variable de entorno)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.use_mock = not self.api_key or self.api_key == "your_gemini_api_key_here"
        
        if not self.use_mock:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                # Usar modelo actualizado - intentar varios nombres (más recientes primero)
                model_names = [
                    'gemini-2.0-flash-exp',
                    'gemini-1.5-flash-latest', 
                    'gemini-1.5-flash',
                    'gemini-1.5-pro-latest',
                    'gemini-1.5-pro',
                    'gemini-pro'
                ]
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        print(f"✅ Gemini API configurada ({model_name})")
                        break
                    except Exception as e:
                        print(f"⚠️  Modelo {model_name} no disponible: {str(e)[:50]}")
                        continue
                else:
                    raise Exception("No se encontró un modelo válido")
            except Exception as e:
                print(f"⚠️  Error configurando Gemini: {e}")
                print("📝 Usando modo mock (templates)")
                self.use_mock = True
        else:
            print("📝 Usando modo mock (templates) - configurar GEMINI_API_KEY para usar API real")
    
    def nl_to_sql(self, natural_language: str) -> str:
        """
        Convierte lenguaje natural a SQL.
        
        Args:
            natural_language: Pregunta en lenguaje natural
        
        Returns:
            Consulta SQL generada
        """
        if self.use_mock:
            return self._mock_nl_to_sql(natural_language)
        
        try:
            # Llamar a Gemini API
            prompt = SYSTEM_PROMPT + f"\nNL: {natural_language}\nSQL:"
            response = self.model.generate_content(prompt)
            sql = response.text.strip()
            
            # Limpiar respuesta (remover markdown si existe)
            sql = self._clean_sql_response(sql)
            
            return sql
            
        except Exception as e:
            print(f"⚠️  Error llamando a Gemini API: {e}")
            print("📝 Fallback a modo mock")
            return self._mock_nl_to_sql(natural_language)
    
    def _clean_sql_response(self, sql: str) -> str:
        """Limpia la respuesta de Gemini (remover markdown, etc.)"""
        # Remover bloques de código markdown
        sql = re.sub(r'```sql\n?', '', sql)
        sql = re.sub(r'```\n?', '', sql)
        
        # Remover líneas de explicación
        lines = sql.split('\n')
        sql_lines = [line for line in lines if not line.strip().startswith('#') 
                     and not line.strip().startswith('--')]
        sql = '\n'.join(sql_lines).strip()
        
        return sql
    
    def _mock_nl_to_sql(self, natural_language: str) -> str:
        """
        Modo mock: genera SQL basado en templates y keywords.
        Útil para desarrollo sin API key.
        """
        nl_lower = natural_language.lower()
        
        # Patrones de camiones por marca
        brands = ["volvo", "scania", "mercedes", "man", "daf", "iveco"]
        for brand in brands:
            if brand in nl_lower and ("cuántos" in nl_lower or "cantidad" in nl_lower or "hay" in nl_lower):
                return f"SELECT COUNT(*) as total, brand FROM trucks WHERE LOWER(brand) = '{brand}' GROUP BY brand LIMIT 1000;"
            elif brand in nl_lower and ("camiones" in nl_lower or "trucks" in nl_lower):
                return f"SELECT * FROM trucks WHERE LOWER(brand) = '{brand}' LIMIT 1000;"
        
        # Patrones de alertas
        if "alertas" in nl_lower and "temperatura" in nl_lower:
            return "SELECT truck_id, COUNT(*) as alerts FROM alerts WHERE alert_type = 'temperature' AND timestamp >= datetime('now', '-7 days') GROUP BY truck_id ORDER BY alerts DESC LIMIT 5;"
        
        elif "promedio" in nl_lower and ("consumo" in nl_lower or "combustible" in nl_lower):
            return "SELECT t.brand, AVG(tele.fuel_level) as avg_fuel_level FROM trucks t JOIN telemetry tele ON t.truck_id = tele.truck_id WHERE tele.timestamp >= datetime('now','-30 days') GROUP BY t.brand;"
        
        elif "viajes" in nl_lower and ("ayer" in nl_lower or "finalizados" in nl_lower):
            return "SELECT COUNT(*) as trips_finished FROM trips WHERE status = 'finished' AND date(end_time) = date('now','-1 day');"
        
        elif "alertas" in nl_lower and "críticas" in nl_lower:
            return "SELECT * FROM alerts WHERE severity = 'critical' ORDER BY timestamp DESC LIMIT 10;"
        
        elif "mantenimiento" in nl_lower:
            return "SELECT * FROM trucks WHERE status = 'maintenance' LIMIT 1000;"
        
        elif "rutas" in nl_lower and "retrasos" in nl_lower:
            return "WITH trip_delays AS (SELECT trip_id, origin, destination, (julianday(end_time) - julianday(start_time)) * 24 as duration_hours FROM trips WHERE status = 'finished') SELECT origin, destination, AVG(duration_hours) as avg_duration FROM trip_delays GROUP BY origin, destination ORDER BY avg_duration DESC LIMIT 5;"
        
        elif "conductor" in nl_lower and "kilómetros" in nl_lower:
            return "SELECT d.name, d.driver_id, SUM(t.distance_km) as total_km FROM drivers d JOIN trucks tr ON d.driver_id = tr.driver_id JOIN trips t ON tr.truck_id = t.truck_id WHERE t.start_time >= datetime('now', '-30 days') GROUP BY d.driver_id ORDER BY total_km DESC LIMIT 1;"
        
        elif "velocidad" in nl_lower and "excesiva" in nl_lower:
            return "SELECT * FROM alerts WHERE alert_type = 'speed' AND timestamp >= datetime('now', '-7 days') ORDER BY timestamp DESC LIMIT 20;"
        
        elif "combustible" in nl_lower and "bajo" in nl_lower:
            return "SELECT DISTINCT t.truck_id, t.plate, t.brand, tele.fuel_level FROM trucks t JOIN telemetry tele ON t.truck_id = tele.truck_id WHERE tele.fuel_level < 20 ORDER BY tele.fuel_level ASC LIMIT 10;"
        
        elif "viajes" in nl_lower and ("largos" in nl_lower or "región" in nl_lower):
            return "SELECT t.region, tr.origin, tr.destination, tr.distance_km FROM trips tr JOIN trucks t ON tr.truck_id = t.truck_id ORDER BY tr.distance_km DESC LIMIT 10;"
        
        # Patrones generales de conteo
        elif "cuántos" in nl_lower or "cantidad" in nl_lower:
            if "camiones" in nl_lower or "trucks" in nl_lower:
                return "SELECT COUNT(*) as total FROM trucks LIMIT 1000;"
            elif "viajes" in nl_lower:
                return "SELECT COUNT(*) as total FROM trips LIMIT 1000;"
            elif "conductores" in nl_lower or "drivers" in nl_lower:
                return "SELECT COUNT(*) as total FROM drivers LIMIT 1000;"
        
        # Default: listar camiones
        else:
            return "SELECT * FROM trucks LIMIT 10;"
    
    def generate_explanation(self, nl_query: str, sql: str, rows: list) -> str:
        """
        Genera explicación inteligente en lenguaje natural de los resultados.
        Analiza los datos y proporciona insights, no solo cuenta filas.
        
        Args:
            nl_query: Pregunta original
            sql: SQL ejecutado
            rows: Resultados obtenidos
        
        Returns:
            Explicación detallada con análisis e insights
        """
        if not rows:
            return "❌ No se encontraron resultados para esta consulta. Intenta reformular tu pregunta o verifica que los datos existan."
        
        num_rows = len(rows)
        
        if self.use_mock:
            return self._generate_smart_mock_explanation(nl_query, sql, rows, num_rows)
        
        try:
            # Preparar muestra de datos (máximo 5 filas para no saturar el prompt)
            sample_rows = rows[:5] if len(rows) > 5 else rows
            
            # Convertir datos a formato legible
            import json
            data_sample = json.dumps(sample_rows, indent=2, ensure_ascii=False)
            
            prompt = f"""Eres un analista de datos experto en logística y flotas de camiones. 

PREGUNTA DEL USUARIO:
{nl_query}

SQL EJECUTADO:
{sql}

RESULTADOS OBTENIDOS ({num_rows} registros):
{data_sample}
{"..." if len(rows) > 5 else ""}

INSTRUCCIONES:
1. Analiza los resultados y genera una explicación en lenguaje natural conversacional
2. Identifica insights clave (máximos, mínimos, promedios, tendencias, patrones)
3. Si es relevante, menciona implicaciones de negocio o recomendaciones
4. Usa un tono profesional pero amigable
5. Máximo 3-4 oraciones
6. Si hay datos numéricos importantes, menciónalos específicamente
7. NO repitas la pregunta, ve directo al análisis

FORMATO DE RESPUESTA:
📊 [Explicación del resultado principal]
💡 [Insight o dato destacado]
[Recomendación u observación adicional si aplica]

Genera la explicación:"""
            
            response = self.model.generate_content(prompt)
            explanation = response.text.strip()
            
            # Agregar conteo de resultados al final si no está mencionado
            if str(num_rows) not in explanation and num_rows > 1:
                explanation += f"\n\n📈 Total de registros encontrados: {num_rows}"
            
            return explanation
            
        except Exception as e:
            print(f"⚠️  Error generando explicación: {e}")
            # Fallback a explicación inteligente sin API
            return self._generate_smart_mock_explanation(nl_query, sql, rows, num_rows)
    
    def _generate_smart_mock_explanation(self, nl_query: str, sql: str, rows: list, num_rows: int) -> str:
        """
        Genera explicación inteligente sin usar API, analizando los datos directamente.
        """
        if num_rows == 0:
            return "❌ No se encontraron resultados para esta consulta."
        
        nl_lower = nl_query.lower()
        explanation_parts = []
        
        # Analizar el tipo de query y los resultados
        try:
            # Detectar agregaciones
            if "count" in sql.lower() and len(rows) == 1 and "count" in str(rows[0]).lower():
                count_value = list(rows[0].values())[0] if isinstance(rows[0], dict) else rows[0][0]
                explanation_parts.append(f"📊 Se encontraron **{count_value}** registros que coinciden con tu consulta.")
            
            # Detectar TOP/LIMIT con ordenamiento
            elif ("order by" in sql.lower() or "top" in nl_lower or "más" in nl_lower or "mayor" in nl_lower) and num_rows > 0:
                first_row = rows[0]
                if isinstance(first_row, dict):
                    # Identificar la columna principal
                    keys = list(first_row.keys())
                    id_col = keys[0] if keys else None
                    value_col = keys[1] if len(keys) > 1 else keys[0]
                    
                    if id_col and value_col:
                        top_id = first_row[id_col]
                        top_value = first_row[value_col]
                        
                        # Detectar el tipo de métrica basándose en la columna y la query
                        value_col_lower = value_col.lower()
                        
                        if "alert" in value_col_lower or "alerta" in nl_lower:
                            explanation_parts.append(f"📊 El camión **{top_id}** tiene el mayor número de alertas: **{top_value}**.")
                        elif "temp" in value_col_lower or ("temperatura" in nl_lower and "alerta" not in nl_lower):
                            explanation_parts.append(f"📊 El camión **{top_id}** registró la mayor temperatura con **{top_value}°C**.")
                        elif "distance" in value_col_lower or "km" in value_col_lower or "kilómetro" in nl_lower or "distancia" in nl_lower:
                            explanation_parts.append(f"📊 El camión **{top_id}** ha recorrido la mayor distancia: **{top_value} km**.")
                        elif "fuel" in value_col_lower or "combustible" in nl_lower:
                            explanation_parts.append(f"📊 El camión **{top_id}** tiene el mayor consumo de combustible: **{top_value}**.")
                        elif "speed" in value_col_lower or "velocidad" in nl_lower:
                            explanation_parts.append(f"📊 El camión **{top_id}** registró la mayor velocidad: **{top_value} km/h**.")
                        else:
                            explanation_parts.append(f"📊 **{top_id}** lidera con un valor de **{top_value}**.")
                        
                        # Mencionar top 3 si hay más
                        if num_rows >= 3:
                            explanation_parts.append(f"💡 Los siguientes en el ranking completan el top {min(num_rows, 3)}.")
            
            # Detectar promedios
            elif "avg" in sql.lower() or "promedio" in nl_lower:
                if num_rows > 0 and isinstance(rows[0], dict):
                    avg_cols = [k for k in rows[0].keys() if 'avg' in k.lower() or 'promedio' in k.lower()]
                    if avg_cols:
                        avg_col = avg_cols[0]
                        values = [row[avg_col] for row in rows if avg_col in row]
                        if values:
                            max_val = max(values)
                            min_val = min(values)
                            avg_val = sum(values) / len(values)
                            
                            max_row = next(row for row in rows if row.get(avg_col) == max_val)
                            min_row = next(row for row in rows if row.get(avg_col) == min_val)
                            
                            group_col = [k for k in rows[0].keys() if k != avg_col][0]
                            
                            explanation_parts.append(f"📊 El promedio general es **{avg_val:.1f}**.")
                            explanation_parts.append(f"💡 **{max_row[group_col]}** tiene el valor más alto ({max_val:.1f}) mientras que **{min_row[group_col]}** el más bajo ({min_val:.1f}).")
            
            # Detectar GROUP BY
            elif "group by" in sql.lower() and num_rows > 1:
                explanation_parts.append(f"📊 Se agruparon los resultados en **{num_rows}** categorías diferentes.")
                if isinstance(rows[0], dict) and len(rows[0]) >= 2:
                    keys = list(rows[0].keys())
                    explanation_parts.append(f"💡 Cada categoría muestra información de **{', '.join(keys[1:])}**.")
            
            # Filtros específicos
            if "mantenimiento" in nl_lower:
                explanation_parts.append("🔧 Estos camiones requieren atención de mantenimiento prioritaria.")
            elif "crítica" in nl_lower or "critical" in sql.lower():
                explanation_parts.append("⚠️ Estas alertas requieren atención inmediata.")
            elif "velocidad" in nl_lower:
                explanation_parts.append("🚨 Considera revisar las políticas de conducción y capacitación de conductores.")
            
        except Exception as e:
            print(f"⚠️  Error en análisis mock: {e}")
        
        # Si no se generó ninguna explicación específica, usar genérica mejorada
        if not explanation_parts:
            if num_rows == 1:
                explanation_parts.append(f"✅ Se encontró **1 resultado** que coincide con tu consulta.")
            else:
                explanation_parts.append(f"✅ Se encontraron **{num_rows} resultados** que coinciden con tu consulta.")
        
        # Agregar conteo final si no está
        if num_rows > 1 and str(num_rows) not in ' '.join(explanation_parts):
            explanation_parts.append(f"\n📈 Total de registros: **{num_rows}**")
        
        return ' '.join(explanation_parts)


# Test del cliente
if __name__ == "__main__":
    print("🧪 Probando Gemini Client...\n")
    
    client = GeminiClient()
    
    test_queries = [
        "¿Qué camión tuvo más alertas de temperatura en la última semana?",
        "Promedio de consumo por marca de camión",
        "Lista de camiones en mantenimiento"
    ]
    
    for query in test_queries:
        print(f"NL: {query}")
        sql = client.nl_to_sql(query)
        print(f"SQL: {sql}")
        print()
