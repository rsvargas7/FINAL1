import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Monitoreo Meteorológico - EAFIT",
    page_icon="Cloud",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILO CSS - TEMA OSCURO PROFESIONAL
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global */
    .main {
        font-family: 'Inter', sans-serif;
        padding: 2rem;
    }
    .stApp {
        background: #0e1117;
        color: #e0e0e0;
    }
    
    /* Títulos */
    .header-title {
        font-size: 2.8rem !important;
        font-weight: 700;
        background: linear-gradient(90deg, #00c6ff, #0070f3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #aaa;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Tarjetas */
    .card {
        background: #1a1f2e;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #2d3748;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin: 1rem 0;
        color: #e0e0e0;
    }
    
    /* Métricas */
    .metric-card {
        background: linear-gradient(135deg, #0070f3, #00c6ff);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(0, 112, 243, 0.3);
    }
    
    /* Inputs */
    .stSelectbox > div > div, .stMultiSelect > div > div {
        background-color: #262730 !important;
        color: #e0e0e0 !important;
        border: 1px solid #3a3f50 !important;
        border-radius: 10px;
    }
    .stSlider > div > div > div {
        background: #0070f3;
    }
    .stButton > button {
        background: #0070f3;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background: #005edc;
    }
    
    /* Tablas */
    .dataframe {
        background: #1a1f2e !important;
        color: #e0e0e0 !important;
    }
    
    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background: #161b22 !important;
        color: #e0e0e0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        font-size: 0.9rem;
        margin-top: 3rem;
        border-top: 1px solid #2d3748;
    }
    
    /* Alertas */
    .stAlert {
        background: #1a1f2e;
        border: 1px solid #3a3f50;
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# TÍTULO PRINCIPAL
# =========================
st.markdown('<h1 class="header-title">Cloud Monitoreo Meteorológico EAFIT</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Presión atmosférica y velocidad del viento en tiempo real</p>', unsafe_allow_html=True)

# =========================
# SIDEBAR - INFORMACIÓN
# =========================
with st.sidebar:
    st.image("https://www.eafit.edu.co/-/media/eafit/images/logos/eafit-logo.png", width=180)
    st.markdown("### Location Ubicación")
    st.markdown("**Universidad EAFIT**")
    st.caption("Lat: 6.2006, Lon: -75.5783")
    st.caption("Altitud: ~1,495 m.s.n.m")
    st.markdown("---")
    st.markdown("### Sensor Sensor")
    st.markdown("- **Tipo:** ESP32 + BME280")
    st.markdown("- **Variables:** Presión, Viento")
    st.markdown("- **Frecuencia:** 1 min")
    st.markdown("---")
    st.success("Sistema en línea")

# =========================
# CARGA DE ARCHIVO
# =========================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### Upload Cargar Archivo CSV")
uploaded_file = st.file_uploader("Selecciona tu archivo de datos", type=['csv'], label_visibility="collapsed")
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        # Leer CSV
        df = pd.read_csv(uploaded_file)
        if df.empty:
            st.error("El archivo CSV está vacío.")
            st.stop()

        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True)

        # Detectar columna de tiempo
        time_col = None
        time_keywords = ['time', 'timestamp', 'fecha', 'hora']
        for col in df.columns:
            if any(kw in col.lower() for kw in time_keywords):
                time_col = col
                break

        if time_col:
            df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
            df = df.dropna(subset=[time_col])
            if df.empty:
                st.error("No se encontraron fechas válidas en la columna de tiempo.")
                st.stop()
            df = df.set_index(time_col)

        # Detectar columnas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            st.error("No se encontraron columnas con datos numéricos.")
            st.info("Asegúrate de que el CSV tenga valores como 1013.5, 3.2, etc.")
            st.stop()

        # Mapeo de nombres amigables
        name_map = {
            'presion': 'Presión atmosférica',
            'pressure': 'Presión atmosférica',
            'presión': 'Presión atmosférica',
            'viento': 'Velocidad del viento',
            'velocidad': 'Velocidad del viento',
            'wind': 'Velocidad del viento',
            'analogico': 'Valor del Sensor',
        }

        df_clean = df.copy()
        for col in numeric_cols:
            col_lower = col.lower()
            for key, name in name_map.items():
                if key in col_lower:
                    df_clean = df_clean.rename(columns={col: name})
                    break

        # Usar nombres amigables o fallback
        final_cols = [c for c in df_clean.columns if c in name_map.values()]
        if not final_cols:
            final_cols = numeric_cols[:2]
            df_clean = df_clean.rename(columns={
                numeric_cols[0]: 'Presión atmosférica',
                numeric_cols[1]: 'Velocidad del viento' if len(numeric_cols) > 1 else 'Variable 2'
            })
            final_cols = ['Presión atmosférica', 'Velocidad del viento'][:len(final_cols)]

        # =========================
        # PESTAÑAS CON NOMBRES CLAROS
        # =========================
        tab1, tab2, tab3, tab4 = st.tabs([
            "Gráficos de Presión y Viento",
            "Estadísticas Meteorológicas",
            "Filtros por Rango de Valores",
            "Ubicación del Sensor"
        ])

        # -----------------------
        # PESTAÑA 1: GRÁFICOS
        # -----------------------
        with tab1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Gráficos en Tiempo Real")
            variable = st.selectbox("Selecciona variable", final_cols, key="chart_var")
            chart_type = st.radio("Tipo de gráfico", ["Línea", "Área", "Barra"], horizontal=True)

            if chart_type == "Línea":
                st.line_chart(df_clean[variable], use_container_width=True, color="#00c6ff")
            elif chart_type == "Área":
                st.area_chart(df_clean[variable], use_container_width=True, color="#0070f3")
            else:
                st.bar_chart(df_clean[variable], use_container_width=True, color="#00c6ff")

            if st.checkbox("Mostrar datos crudos"):
                st.dataframe(df_clean[final_cols], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------
        # PESTAÑA 2: ESTADÍSTICAS
        # -----------------------
        with tab2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Resumen Estadístico")
            cols = st.columns(len(final_cols))
            for i, var in enumerate(final_cols):
                with cols[i]:
                    stats = df_clean[var].describe()
                    unit = 'hPa' if 'Presión' in var else 'm/s'
                    st.markdown(f"<div class='metric-card'>", unsafe_allow_html=True)
                    st.metric(var, f"{stats['mean']:.2f} {unit}")
                    st.caption(f"Máx: {stats['max']:.1f} | Mín: {stats['min']:.1f}")
                    st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------
        # PESTAÑA 3: FILTROS
        # -----------------------
        with tab3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Filtros Interactivos")
            var_filter = st.selectbox("Filtrar por variable", final_cols, key="filter_var")
            min_val, max_val = df_clean[var_filter].min(), df_clean[var_filter].max()
            col1, col2 = st.columns(2)
            with col1:
                low = st.slider("Valor mínimo", float(min_val), float(max_val), float(min_val), step=0.1)
            with col2:
                high = st.slider("Valor máximo", float(min_val), float(max_val), float(max_val), step=0.1)

            filtered = df_clean[(df_clean[var_filter] >= low) & (df_clean[var_filter] <= high)]
            st.success(f"**{len(filtered)} registros** cumplen el filtro.")
            st.dataframe(filtered[final_cols], use_container_width=True)

            csv = filtered.to_csv().encode('utf-8')
            st.download_button(
                "Download Descargar datos filtrados",
                data=csv,
                file_name=f"datos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------
        # PESTAÑA 4: UBICACIÓN
        # -----------------------
        with tab4:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Ubicación del Sensor")
            st.map(pd.DataFrame({'lat': [6.2006], 'lon': [-75.5783]}), zoom=16)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Location Coordenadas")
                st.write("**Latitud:** 6.2006° N")
                st.write("**Longitud:** -75.5783° W")
                st.write("**Altitud:** 1,495 m.s.n.m")
            with col2:
                st.markdown("#### Sensor Detalles del Sensor")
                st.write("**Modelo:** ESP32 + BME280")
                st.write("**Ubicación:** Edificio de Ingeniería")
                st.write("**Frecuencia:** 1 medición/min")
            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
        st.info("Posibles causas:\n"
                "- Columna con texto no numérico\n"
                "- Nombres con espacios o caracteres especiales\n"
                "- Archivo corrupto o mal formateado")

else:
    st.info("Upload Por favor, carga un archivo CSV para comenzar.")
    st.code("""
Time,analogico ESP32,velocidad viento
2025-11-11 12:00:00,1013.5,3.2
2025-11-11 12:01:00,1013.2,3.5
2025-11-11 12:02:00,1013.0,4.0
    """)

# =========================
# FOOTER
# =========================
st.markdown("""
<div class='footer'>
    <p>Cloud Desarrollado para monitoreo ambiental urbano | 
    <strong>Universidad EAFIT</strong> | Medellín, Colombia</p>
</div>
""", unsafe_allow_html=True)
