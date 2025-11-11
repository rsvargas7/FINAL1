import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Monitoreo Meteorológico - EAFIT",
    page_icon="⛈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILO CSS - TEMA OSCURO + ICONOS
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
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
    
    /* Tarjetas de estadísticas */
    .stat-card {
        background: linear-gradient(135deg, #1e3a8a, #1e40af);
        color: white;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 6px 16px rgba(30, 58, 138, 0.4);
        transition: transform 0.2s;
    }
    .stat-card:hover {
        transform: translateY(-4px);
    }
    .stat-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
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
        padding: 0.6rem 1.2rem;
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
</style>
""", unsafe_allow_html=True)

# =========================
# TÍTULO CON EMOJIS
# =========================
st.markdown('<h1 class="header-title">⛈️ Monitoreo Meteorológico EAFIT ⛈️</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Presión atmosférica y velocidad del viento en tiempo real</p>', unsafe_allow_html=True)

# =========================
# SIDEBAR
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
uploaded_file = st.file_uploader("Selecciona tu archivo", type=['csv'], label_visibility="collapsed")
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        if df.empty:
            st.error("El archivo está vacío.")
            st.stop()

        # Limpiar columnas
        df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

        # Detectar tiempo
        time_col = None
        for col in df.columns:
            if any(kw in col.lower() for kw in ['time', 'fecha', 'timestamp', 'hora']):
                time_col = col
                break

        if time_col:
            df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
            df = df.dropna(subset=[time_col])
            df = df.set_index(time_col)

        # Columnas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            st.error("No hay datos numéricos.")
            st.stop()

        # Mapeo de nombres
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
            for key, name in name_map.items():
                if key in col.lower():
                    df_clean = df_clean.rename(columns={col: name})
                    break

        final_cols = [c for c in df_clean.columns if c in name_map.values()]
        if not final_cols:
            final_cols = numeric_cols[:2]
            df_clean = df_clean.rename(columns={
                numeric_cols[0]: 'Presión atmosférica',
                numeric_cols[1]: 'Velocidad del viento' if len(numeric_cols) > 1 else 'Variable 2'
            })
            final_cols = ['Presión atmosférica', 'Velocidad del viento'][:len(final_cols)]

        # =========================
        # PESTAÑAS CON EMOJIS Y SENTIDO
        # =========================
        tab1, tab2, tab3, tab4 = st.tabs([
            "🍃Gráficos de Presión y Viento🍃",
            "☄️Estadísticas Meteorológicas☄️",
            "🎯Filtros por Rango de Valores🎯",
            "📍Ubicación del Sensor📍"
        ])

        # -----------------------
        # PESTAÑA 1: GRÁFICOS
        # -----------------------
        with tab1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Gráficos en Tiempo Real")
            variable = st.selectbox("Selecciona variable", final_cols, key="chart")
            chart_type = st.radio("Tipo", ["Línea", "Área", "Barra"], horizontal=True)

            if chart_type == "Línea":
                st.line_chart(df_clean[variable], use_container_width=True, color="#00c6ff")
            elif chart_type == "Área":
                st.area_chart(df_clean[variable], use_container_width=True, color="#0070f3")
            else:
                st.bar_chart(df_clean[variable], use_container_width=True, color="#00c6ff")

            if st.checkbox("Mostrar datos"):
                st.dataframe(df_clean[final_cols], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------
        # PESTAÑA 2: ESTADÍSTICAS (¡RENOVADA!)
        # -----------------------
        with tab2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Estadísticas Meteorológicas")

            for var in final_cols:
                stats = df_clean[var].describe()
                unit = 'hPa' if 'Presión' in var else 'm/s'
                icon = "Barometer" if 'Presión' in var else "Wind"

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-icon">{icon}</div>
                        <div class="stat-value">{stats['mean']:.2f}</div>
                        <div class="stat-label">Promedio {unit}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-icon">Up Arrow</div>
                        <div class="stat-value">{stats['max']:.2f}</div>
                        <div class="stat-label">Máximo {unit}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-icon">Down Arrow</div>
                        <div class="stat-value">{stats['min']:.2f}</div>
                        <div class="stat-label">Mínimo {unit}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-icon">Sigma</div>
                        <div class="stat-value">{stats['std']:.2f}</div>
                        <div class="stat-label">Desviación {unit}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------
        # PESTAÑA 3: FILTROS
        # -----------------------
        with tab3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Filtros por Rango de Valores")
            var = st.selectbox("Filtrar por", final_cols, key="f")
            minv, maxv = df_clean[var].min(), df_clean[var].max()
            col1, col2 = st.columns(2)
            with col1:
                low = st.slider("Mínimo", float(minv), float(maxv), float(minv), step=0.1)
            with col2:
                high = st.slider("Máximo", float(minv), float(maxv), float(maxv), step=0.1)

            filtered = df_clean[(df_clean[var] >= low) & (df_clean[var] <= high)]
            st.success(f"**{len(filtered)} registros** filtrados")
            st.dataframe(filtered[final_cols], use_container_width=True)

            csv = filtered.to_csv().encode('utf-8')
            st.download_button(
                "Download Descargar",
                data=csv,
                file_name=f"filtrado_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
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
                st.write("**Lat:** 6.2006° N")
                st.write("**Lon:** -75.5783° W")
                st.write("**Alt:** 1,495 m.s.n.m")
            with col2:
                st.markdown("#### Sensor Sensor")
                st.write("**Modelo:** ESP32 + BME280")
                st.write("**Edificio:** Ingeniería")
            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Verifica el formato del CSV.")

else:
    st.info("Upload Carga un archivo CSV para comenzar.")
    st.code("""
Time,analogico ESP32,velocidad viento
2025-11-11 12:00:00,1013.5,3.2
2025-11-11 12:01:00,1013.2,3.5
    """)

# =========================
# FOOTER
# =========================
st.markdown("""
<div class='footer'>
    <p>Cloud Desarrollado para EAFIT | Medellín, Colombia</p>
</div>
""", unsafe_allow_html=True)
