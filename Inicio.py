import pandas as pd
import streamlit as st
from PIL import Image
import numpy as np
from datetime import datetime

# =========================
# Configuración de la página
# =========================
st.set_page_config(
    page_title="Análisis Meteorológico - EAFIT",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Estilos CSS Personalizados
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main {
        padding: 2rem;
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #e0f7fa, #ffffff);
    }
    .header-title {
        font-size: 2.8rem !important;
        font-weight: 700;
        background: linear-gradient(90deg, #1e88e5, #42a5f5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #42a5f5, #1e88e5);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
    }
    .stSelectbox > div > div {
        background-color: #f0f7ff;
        border-radius: 10px;
    }
    .stSlider > div > div > div {
        background: #42a5f5;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #777;
        font-size: 0.9rem;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Título y Descripción
# =========================
st.markdown('<h1 class="header-title">🌤️ Análisis Meteorológico en Tiempo Real</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Monitoreo de sensores ambientales en la Universidad EAFIT, Medellín</p>', unsafe_allow_html=True)

# =========================
# Sidebar - Información
# =========================
with st.sidebar:
    st.image("https://www.eafit.edu.co/-/media/eafit/images/logos/eafit-logo.png", width=200)
    st.markdown("### 🌍 **Ubicación**")
    st.markdown("**Universidad EAFIT**")
    st.caption("📍 Lat: 6.2006, Lon: -75.5783")
    st.caption("🗻 Altitud: ~1,495 m.s.n.m")
    st.markdown("---")
    st.markdown("### 📡 **Sensor**")
    st.markdown("- **Tipo:** ESP32 + BME280/DHT22")
    st.markdown("- **Variables:** Presión, Viento")
    st.markdown("- **Frecuencia:** 1 min")
    st.markdown("---")
    st.markdown("### ⚡ **Estado**")
    st.success("Sistema en línea")

# =========================
# Datos del mapa
# =========================
eafit_location = pd.DataFrame({
    'lat': [6.2006],
    'lon': [-75.5783],
    'size': [50],
    'color': ['#1e88e5']
})

# =========================
# Carga de archivo
# =========================
st.markdown("### 📂 Cargar Datos del Sensor")
uploaded_file = st.file_uploader("Seleccione archivo CSV con datos de sensores", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Detectar columna de tiempo
        time_col = None
        if 'Time' in df.columns:
            time_col = 'Time'
        elif 'time' in df.columns:
            time_col = 'time'
        elif 'Timestamp' in df.columns:
            time_col = 'Timestamp'
        elif df.columns[0].lower() in ['time', 'timestamp', 'fecha']:
            time_col = df.columns[0]

        if time_col:
            df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
            df = df.dropna(subset=[time_col])
            df = df.set_index(time_col)

        # Detectar variables numéricas (excluyendo lat/lon si existen)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) == 0:
            st.error("No se encontraron columnas numéricas en el archivo.")
            st.stop()

        # Mapeo amigable de variables
        variable_names = {
            'pressure': 'Presión atmosférica',
            'presion': 'Presión atmosférica',
            'presión': 'Presión atmosférica',
            'wind_speed': 'Velocidad del viento',
            'velocidad': 'Velocidad del viento',
            'viento': 'Velocidad del viento',
            'vel_viento': 'Velocidad del viento'
        }

        # Renombrar columnas
        df_renamed = df.copy()
        for col in numeric_cols:
            col_lower = col.lower()
            for key, name in variable_names.items():
                if key in col_lower:
                    df_renamed = df_renamed.rename(columns={col: name})
                    break

        # Actualizar lista de columnas numéricas renombradas
        final_cols = [col for col in df_renamed.columns if col in variable_names.values()]
        if not final_cols:
            final_cols = numeric_cols[:2]  # Fallback
            df_renamed = df_renamed.rename(columns={numeric_cols[0]: 'Presión atmosférica'})
            if len(numeric_cols) > 1:
                df_renamed = df_renamed.rename(columns={numeric_cols[1]: 'Velocidad del viento'})

        # =========================
        # Pestañas
        # =========================
        tab1, tab2, tab3, tab4 = st.tabs(["📈 **Gráficos**", "📊 **Estadísticas**", "🔍 **Filtros**", "🗺️ **Mapa**"])

        with tab1:
            st.markdown("### 📊 Visualización de Variables")
            variable = st.selectbox("Seleccione variable para graficar", final_cols)

            col1, col2 = st.columns([3, 1])
            with col1:
                chart_type = st.radio("Tipo de gráfico", ["Línea", "Área", "Barra"], horizontal=True)

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"**Unidad:** {'hPa' if 'Presión' in variable else 'm/s'}")

            if chart_type == "Línea":
                st.line_chart(df_renamed[variable], use_container_width=True)
            elif chart_type == "Área":
                st.area_chart(df_renamed[variable], use_container_width=True)
            else:
                st.bar_chart(df_renamed[variable], use_container_width=True)

            if st.checkbox("Mostrar tabla de datos crudos"):
                st.dataframe(df_renamed[final_cols], use_container_width=True)

        with tab2:
            st.markdown("### 📈 Estadísticas por Variable")
            selected_stats = st.multiselect("Variables para estadísticas", final_cols, default=final_cols[:2])

            cols = st.columns(len(selected_stats))
            for i, var in enumerate(selected_stats):
                with cols[i]:
                    stats = df_renamed[var].describe()
                    unidad = 'hPa' if 'Presión' in var else 'm/s'
                    st.markdown(f"<div class='metric-card'>", unsafe_allow_html=True)
                    st.metric(f"**{var}**", f"{stats['mean']:.2f} {unidad}")
                    st.markdown(f"_Máx: {stats['max']:.2f} | Mín: {stats['min']:.2f}_")
                    st.markdown(f"_Std: {stats['std']:.2f}_")
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### 📋 Resumen Detallado")
            st.dataframe(df_renamed[selected_stats].describe(), use_container_width=True)

        with tab3:
            st.markdown("### 🔧 Filtros Interactivos")
            variable_filter = st.selectbox("Variable para filtrar", final_cols, key="filter_var")

            min_val = float(df_renamed[variable_filter].min())
            max_val = float(df_renamed[variable_filter].max())

            col1, col2 = st.columns(2)
            with col1:
                lower = st.slider("Valor mínimo", min_val, max_val, min_val, step=0.1)
            with col2:
                upper = st.slider("Valor máximo", min_val, max_val, max_val, step=0.1)

            filtered = df_renamed[(df_renamed[variable_filter] >= lower) & (df_renamed[variable_filter] <= upper)]
            st.success(f"**{len(filtered)} registros** cumplen el filtro.")

            st.dataframe(filtered[final_cols], use_container_width=True)

            csv = filtered.to_csv().encode('utf-8')
            st.download_button(
                "📥 Descargar datos filtrados",
                data=csv,
                file_name=f"datos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

        with tab4:
            st.markdown("### 🗺️ Ubicación del Sensor")
            st.map(eafit_location, zoom=16)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### 🌍 Coordenadas")
                st.markdown("**Latitud:** 6.2006° N")
                st.markdown("**Longitud:** -75.5783° W")
                st.markdown("**Altitud:** 1,495 m.s.n.m")
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### 📡 Información del Sensor")
                st.markdown("**Modelo:** ESP32 + BME280")
                st.markdown("**Variables:** Presión, Viento")
                st.markdown("**Ubicación:** Edificio de Ingeniería")
                st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
        st.info("Asegúrate de que el CSV tenga columnas con nombres como 'Time', 'pressure', 'wind_speed', etc.")

else:
    st.info("👈 Por favor, carga un archivo CSV para comenzar el análisis.")
    st.markdown("#### Ejemplo de estructura esperada:")
    st.code("""
Time,pressure,wind_speed
2025-11-11 12:00:00,1013.25,3.5
2025-11-11 12:01:00,1013.10,4.1
...
    """)

# =========================
# Footer
# =========================
st.markdown("""
<div class='footer'>
    <hr style='border-top: 1px solid #ddd;'>
    <p>🌱 Desarrollado para el monitoreo ambiental urbano | 
    <strong>Universidad EAFIT</strong> | Medellín, Colombia</p>
</div>
""", unsafe_allow_html=True)
