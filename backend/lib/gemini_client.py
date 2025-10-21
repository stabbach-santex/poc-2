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
        Genera explicación en lenguaje natural de los resultados.
        
        Args:
            nl_query: Pregunta original
            sql: SQL ejecutado
            rows: Resultados obtenidos
        
        Returns:
            Explicación en texto
        """
        if not rows:
            return "No se encontraron resultados para esta consulta."
        
        num_rows = len(rows)
        
        if self.use_mock:
            return f"Se encontraron {num_rows} resultado(s) para tu consulta."
        
        try:
            prompt = f"""Basándote en la siguiente consulta y resultados, genera una explicación breve en español:

Pregunta: {nl_query}
SQL ejecutado: {sql}
Número de resultados: {num_rows}

Genera una explicación de 1-2 oraciones sobre qué muestran estos resultados."""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"⚠️  Error generando explicación: {e}")
            return f"Se encontraron {num_rows} resultado(s) para tu consulta."


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
