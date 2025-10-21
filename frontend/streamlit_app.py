"""
Streamlit UI para LogiQ AI
Interfaz de chat para consultar el data warehouse logístico.
"""

import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="LogiQ AI",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración
API_URL = "http://localhost:8000"
USER_ID = "demo_user"

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .query-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .sql-box {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🚛 LogiQ AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Consulta tu data warehouse logístico en lenguaje natural</div>', unsafe_allow_html=True)

# Sidebar con información
with st.sidebar:
    st.header("ℹ️ Información")
    
    # Health check
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            health = response.json()
            st.success("✅ API Conectada")
            if "trucks_count" in health:
                st.metric("Camiones en DB", health["trucks_count"])
        else:
            st.error("❌ API no disponible")
    except:
        st.error("❌ No se puede conectar al backend")
        st.info("Ejecutar: ./run_backend.sh")
    
    st.divider()
    
    st.header("📊 Schema")
    st.markdown("""
    **Tablas disponibles:**
    - `trucks` - Información de camiones
    - `drivers` - Conductores
    - `trips` - Viajes realizados
    - `telemetry` - Telemetría en tiempo real
    - `alerts` - Alertas y eventos
    """)
    
    st.divider()
    
    st.header("💡 Ejemplos")
    st.markdown("""
    - ¿Qué camión tuvo más alertas?
    - Promedio de consumo por marca
    - Viajes finalizados ayer
    - Alertas críticas recientes
    - Camiones en mantenimiento
    """)

# Queries de ejemplo (botones rápidos)
st.subheader("🚀 Queries Rápidas")

col1, col2, col3 = st.columns(3)

example_queries = [
    "¿Qué camión tuvo más alertas de temperatura en la última semana?",
    "Promedio de consumo por marca de camión en los últimos 30 días",
    "¿Cuántos viajes finalizados hubo ayer?",
    "Mostrar las 10 últimas alertas críticas",
    "Lista de camiones actualmente en mantenimiento",
    "Top 5 rutas con más retrasos",
    "¿Cuál es el conductor con más kilómetros recorridos este mes?",
    "Alertas de velocidad excesiva en la última semana",
    "Camiones con nivel de combustible bajo (< 20%)"
]

# Mostrar 3 botones en fila
with col1:
    if st.button("🔥 Alertas de temperatura", use_container_width=True):
        st.session_state.query_input = example_queries[0]

with col2:
    if st.button("⛽ Consumo por marca", use_container_width=True):
        st.session_state.query_input = example_queries[1]

with col3:
    if st.button("🚨 Alertas críticas", use_container_width=True):
        st.session_state.query_input = example_queries[3]

# Más botones
col4, col5, col6 = st.columns(3)

with col4:
    if st.button("🔧 Camiones en mantenimiento", use_container_width=True):
        st.session_state.query_input = example_queries[4]

with col5:
    if st.button("⏱️ Rutas con retrasos", use_container_width=True):
        st.session_state.query_input = example_queries[5]

with col6:
    if st.button("🏃 Top conductor", use_container_width=True):
        st.session_state.query_input = example_queries[6]

st.divider()

# Input principal
st.subheader("💬 Tu Consulta")

# Usar session_state para mantener el valor del input
if 'query_input' not in st.session_state:
    st.session_state.query_input = ""

query = st.text_area(
    "Escribe tu pregunta en lenguaje natural:",
    value=st.session_state.query_input,
    height=100,
    placeholder="Ejemplo: ¿Cuántos camiones están activos en la región Norte?"
)

# Botón de enviar
col_send, col_clear = st.columns([3, 1])

with col_send:
    send_button = st.button("🔍 Consultar", type="primary", use_container_width=True)

with col_clear:
    if st.button("🗑️ Limpiar", use_container_width=True):
        st.session_state.query_input = ""
        st.rerun()

# Procesar query
if send_button and query:
    with st.spinner("🤔 Procesando tu consulta..."):
        try:
            # Llamar a la API
            response = requests.post(
                f"{API_URL}/query",
                json={
                    "user": USER_ID,
                    "nl": query
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Mostrar resultados
                st.success("✅ Consulta procesada exitosamente")
                
                # Métricas
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric("⏱️ Tiempo", f"{result['execution_time_ms']:.0f} ms")
                with col_m2:
                    st.metric("📊 Resultados", result['rows_count'])
                with col_m3:
                    st.metric("🔍 Estado", "Exitoso")
                
                st.divider()
                
                # Explicación
                st.subheader("💡 Explicación")
                st.info(result['explanation'])
                
                # SQL generado (colapsable)
                with st.expander("🔍 Ver SQL Generado", expanded=False):
                    st.code(result['sql'], language='sql')
                
                # Resultados en tabla
                st.subheader("📊 Resultados")
                
                if result['rows_count'] > 0:
                    df = pd.DataFrame(result['rows'])
                    
                    # Mostrar tabla
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Opción de descargar
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv,
                        file_name=f"logiq_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    # Visualización básica si hay datos numéricos
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if len(numeric_cols) > 0 and len(df) > 1:
                        st.subheader("📈 Visualización")
                        
                        # Intentar crear gráfico
                        try:
                            if len(df.columns) >= 2:
                                chart_col = st.selectbox(
                                    "Selecciona columna para graficar:",
                                    numeric_cols
                                )
                                st.bar_chart(df.set_index(df.columns[0])[chart_col])
                        except:
                            pass
                else:
                    st.warning("No se encontraron resultados para esta consulta.")
            
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                st.error(f"❌ Error: {error_detail}")
        
        except requests.exceptions.Timeout:
            st.error("❌ Timeout: La consulta tardó demasiado. Intenta con una consulta más simple.")
        
        except requests.exceptions.ConnectionError:
            st.error("❌ No se puede conectar al backend. Asegúrate de que esté corriendo (./run_backend.sh)")
        
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")

elif send_button:
    st.warning("⚠️ Por favor escribe una consulta primero.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🚛 <strong>LogiQ AI</strong> - Prototipo MVP para GLAC Hackathon 2025</p>
    <p style='font-size: 0.9rem;'>Powered by Gemini AI & FastAPI</p>
</div>
""", unsafe_allow_html=True)
