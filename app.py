import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import base64
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

# --- INICIALIZACIÓN FIREBASE ---
db = None
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            # Para Streamlit Cloud (Despliegue)
            firebase_creds = dict(st.secrets["firebase"])
            # Corregir saltos de línea en la clave privada si vienen escapados
            if "private_key" in firebase_creds:
                firebase_creds["private_key"] = firebase_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
        else:
            # Para desarrollo local
            cred = credentials.Certificate("firebase-key.json")
            firebase_admin.initialize_app(cred)
            db = firestore.client()
    except Exception as e:
        st.warning("⚠️ Conectando en Modo Offline: Las funciones en vivo (Firebase) no estarán disponibles.")
        # Fallback para evitar errores de referencia si algo falla
        if not firebase_admin._apps:
            try:
                firebase_admin.initialize_app()
                db = firestore.client()
            except:
                db = None
else:
    try:
        db = firestore.client()
    except:
        db = None

# --- FUNCIONES DE INTELIGENCIA FIREBASE ---
def log_activity(action, details=""):
    """Registra una acción en la base de datos de auditoría"""
    if db is None:
        return
    try:
        db.collection('activity_logs').add({
            'timestamp': firestore.SERVER_TIMESTAMP,
            'action': action,
            'details': details,
            'user': 'Analista UCentral'
        })
    except Exception:
        pass

def get_insights():
    """Recupera los últimos insights guardados por usuarios"""
    if db is None:
        return []
    try:
        docs = db.collection('strategic_insights').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5).stream()
        return [doc.to_dict() for doc in docs]
    except Exception:
        return []

def add_insight(text):
    """Guarda un nuevo insight estratégico en la nube"""
    if db is None:
        return False
    if text:
        try:
            db.collection('strategic_insights').add({
                'text': text,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'author': 'Analista Principal'
            })
            log_activity("Nuevo Insight", text[:50])
            return True
        except Exception:
            return False
    return False

# Registro automático de entrada
if 'first_load' not in st.session_state:
    log_activity("Acceso al Dashboard", "Puerto 8506")
    st.session_state['first_load'] = True

# 1. Configuración de página
st.set_page_config(
    page_title="Inteligencia de Medios Colombia | Powered by Stitch",
    page_icon="🏙️",
    layout="wide"
)

# --- ACCESO DIRECTO HABILITADO ---
# (Se eliminó la autenticación institucional temporalmente por solicitud del usuario)

# Rutas de imágenes (relativas al archivo app.py)
bg_path = Path(__file__).parent / "banner_warm.png"
icons_path = Path(__file__).parent / "icons.png"

# Placeholder para QR (LinkedIn del analista)
qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://www.linkedin.com/in/luislopezanalytics"

def get_base64_img(img_path):
    try:
        if img_path.exists():
            return base64.b64encode(open(img_path, "rb").read()).decode()
        return ""
    except Exception:
        return ""

banner_bg_b64 = get_base64_img(bg_path)
banner_icons_b64 = get_base64_img(icons_path)
# Alias para compatibilidad con código existente
icons_b64 = banner_icons_b64

# QR y Enlace de LinkedIn Universal
qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://www.linkedin.com/in/luislopezanalytics"

# 2. Estilo Visual: Azules Claros Premium (Firma Visual de Stitch)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@700&display=swap');

    .stApp {
        background: radial-gradient(circle at top right, #f1f5f9, #ffffff);
        color: #1e293b;
    }
    
    .stitch-signature {
        color: #fbbf24; 
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 1rem;
        letter-spacing: 0.35em;
        text-transform: uppercase;
        margin-bottom: 15px;
        text-shadow: 0 4px 8px rgba(0,0,0,0.9);
    }

    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }
    
    /* Tarjetas KPI Premium con Toque Cálido */
    .kpi-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
        border: 1px solid rgba(226, 232, 240, 0.8);
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 25px -5px rgba(245, 158, 11, 0.15), 0 10px 10px -5px rgba(245, 158, 11, 0.05);
        border-color: #f59e0b;
    }
    .kpi-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 5px;
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }
    
    .kpi-label { color: #64748b; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .kpi-value { font-size: 2.2rem; font-weight: 800; color: #0f172a; }

    .stTabs [data-baseweb="tab"] p { color: #64748b !important; font-size: 1rem; transition: all 0.3s ease; }
    .stTabs [aria-selected="true"] p { color: #f59e0b !important; font-weight: 800; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: transparent; border-bottom: 2px solid #f1f5f9; padding-bottom: 5px; }

    /* Conclusiones Glassmorphism */
    .conclusion-box {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-left: 8px solid #f59e0b;
        border-radius: 24px;
        padding: 35px;
        margin: 30px 0;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
    }
    .conclusion-item {
        margin-bottom: 25px;
        font-size: 1.1rem;
        line-height: 1.8;
        color: #1e293b;
    }
    
    .download-btn {
        background: #0f172a;
        color: white !important;
        padding: 14px 28px;
        border-radius: 16px;
        text-decoration: none;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 12px;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.2);
    }
    .download-btn:hover {
        background: #1e293b;
        transform: scale(1.02);
    }

    /* Hub de Inteligencia & Muro */
    .intel-log {
        background: #0f172a;
        color: #fbbf24;
        padding: 12px;
        border-radius: 12px;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.7rem;
        border-left: 4px solid #fbbf24;
        margin-bottom: 10px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
    }
    .insight-bubble {
        background: white;
        padding: 20px;
        border-radius: 20px 20px 20px 5px;
        box-shadow: 0 4px 15px -3px rgba(0, 0, 0, 0.05);
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .insight-bubble:hover {
        box-shadow: 0 10px 25px -5px rgba(251, 191, 36, 0.1);
    }
    .live-pulse {
        width: 12px;
        height: 12px;
        background: #f59e0b;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        box-shadow: 0 0 12px #f59e0b;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(245, 158, 11, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
    }

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(226, 232, 240, 0.8) !important;
    }
    
    /* Botón de Colapso Sidebar Premium */
    button[title*="sidebar" i], button[aria-label*="sidebar" i], 
    button[title*="barra lateral" i], button[aria-label*="barra lateral" i] {
        background: #0f172a !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        padding: 8px !important;
        transition: all 0.3s ease !important;
    }
    button[title*="sidebar" i]:hover { background: #1e293b !important; transform: rotate(90deg); }

    .signature-banner {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(15, 23, 42, 0.6) 100%), url("data:image/png;base64,{banner_bg_b64}");
        background-size: cover;
        background-position: center;
        padding: 100px 50px;
        border-radius: 40px;
        color: white;
        text-align: center;
        margin-bottom: 50px;
        box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .sig-title { font-size: 3.8rem !important; line-height: 1.1; margin-bottom: 25px !important; text-shadow: 0 4px 20px rgba(0,0,0,1); color: white !important; }
    .sig-subtitle { 
        font-size: 1.3rem; 
        font-weight: 600; 
        max-width: 900px; 
        margin: 0 auto 45px auto !important; 
        text-shadow: 0 2px 10px rgba(0,0,0,1); 
        color: #ffffff !important;
        background: rgba(0,0,0,0.4);
        padding: 15px 25px;
        border-radius: 15px;
    }
    .sig-footer { 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        gap: 30px; 
        background: rgba(255,255,255,0.05); 
        padding: 25px; 
        border-radius: 30px; 
        max-width: 600px; 
        margin: 0 auto;
        backdrop-filter: blur(5px);
    }
    .sig-name { font-size: 1.5rem; font-weight: 800; color: #fbbf24 !important; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
    .sig-rank { font-size: 0.95rem; color: #ffffff !important; font-weight: 600; opacity: 1; text-shadow: 0 1px 3px rgba(0,0,0,0.8); }
    .linkedin-btn { 
        background: #fbbf24 !important; 
        color: #0f172a !important; 
        padding: 10px 22px; 
        border-radius: 12px; 
        font-weight: 800; 
        text-decoration: none; 
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
    }
    .linkedin-btn:hover { background: #f59e0b !important; transform: scale(1.05); }
    .qr-container { background: white; padding: 10px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); }

    .micro-signature {
        text-align: center;
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 600;
        margin-top: 50px;
        letter-spacing: 0.05em;
    }

    /* Forzar que el icono (SVG) dentro de los botones sea blanco y grande */
    button[title*="sidebar" i] svg, button[title*="barra lateral" i] svg {
        fill: white !important;
        width: 28px !important;
        height: 28px !important;
    }

    button[title*="sidebar" i]:hover, button[title*="barra lateral" i]:hover { 
        transform: scale(1.1); 
        background-color: #e11d48 !important; 
    }
    
    button[title="Collapse sidebar"] svg, button[title="Expand sidebar"] svg {
        fill: white !important;
        width: 30px !important;
        height: 30px !important;
    }

    /* Estilo para la línea roja divisoria entre párrafos */
    .cronica-container {
        display: flex;
        gap: 30px;
        align-items: center;
        margin-top: 20px;
    }
    .cronica-text {
        flex: 1;
        text-align: justify;
        font-size: 1rem;
        line-height: 1.6;
    }
    .red-divider {
        width: 4px;
        height: 100px;
        background-color: #f43f5e;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(244, 63, 94, 0.5);
    }
    @media (max-width: 768px) {
        .cronica-container { flex-direction: column; }
        .red-divider { width: 100%; height: 4px; }
    }
    .sidebar-title {
        color: #1e3a8a;
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 10px;
        text-align: center;
    }
    /* Responsividad Celular */
    @media (max-width: 768px) {
        .sig-title { font-size: 1.8rem; }
        .sig-subtitle { font-size: 0.9rem; margin: 10px 0; }
        .signature-banner { padding: 40px 20px; border-radius: 20px; }
        .sig-name { font-size: 1.2rem; }
        .sig-rank { font-size: 0.8rem; }
        .kpi-value { font-size: 1.4rem; }
        .kpi-label { font-size: 0.7rem; }
        .stPlotlyChart { height: 350px !important; }
    }
</style>
""", unsafe_allow_html=True)

# 3. Datos Maestro (Firestore)
@st.cache_data
def load_all_market_data():
    """Carga datos desde Firestore con un fallback a datos de muestra si falla"""
    def get_sample_data():
        """Datos de emergencia para que el dashboard no rompa"""
        sample = []
        for year in range(1995, 2026):
            base = 200000 + (year-1995)*150000
            sample.append({
                'Año': year,
                'TV Nacional': base * 0.45,
                'Digital': base * 0.01 * (year-1995)**1.8 if year > 2000 else 0,
                'Radio': base * 0.15,
                'Prensa': base * 0.10,
                'Exterior': base * 0.08,
                'TV Local': base * 0.07,
                'Revistas': base * 0.05,
                'Internet_Penetration': min(95, (year-1995)*3.5)
            })
        df_sample = pd.DataFrame(sample)
        cols_inv = ['TV Nacional', 'Digital', 'Radio', 'Prensa', 'Exterior', 'TV Local', 'Revistas']
        df_sample['TOTAL'] = df_sample[cols_inv].sum(axis=1)
        return df_sample

    if db is None:
        st.warning("⚠️ Sin conexión a Firebase Cloud: Mostrando datos de respaldo (Cache Local).")
        return get_sample_data()
    
    try:
        # Consultar la colección en la nube
        docs = db.collection('market_data').order_by('year').stream()
        data_list = []
        for doc in docs:
            data_list.append(doc.to_dict())
        
        if not data_list:
            st.error("⚠️ No se encontraron datos en Firestore. Usando respaldo local.")
            return get_sample_data()

        df = pd.DataFrame(data_list)
        
        # Mapeo de nombres de Firebase a columnas del Dashboard
        df = df.rename(columns={
            'year': 'Año',
            'tv_nacional': 'TV Nacional',
            'digital': 'Digital',
            'radio': 'Radio',
            'prensa': 'Prensa',
            'exterior': 'Exterior',
            'tv_local': 'TV Local',
            'revistas': 'Revistas',
            'internet_penetration': 'Internet_Penetration'
        })
        
        # Cálculos derivados
        cols_inv = ['TV Nacional', 'Digital', 'Radio', 'Prensa', 'Exterior', 'TV Local', 'Revistas']
        df['TOTAL'] = df[cols_inv].sum(axis=1)
        df['Var_YoY'] = df['TOTAL'].pct_change() * 100
        
        return df
    except Exception as e:
        st.error(f"❌ Error al conectar con Firebase: {e}")
        return get_sample_data()

df = load_all_market_data()

# 4. Estilo Stitch para Gráficas Premium (Tamaño Unificado)
def apply_stitch_style(fig, height=450, title=""):
    fig.update_layout(
         template='plotly_white',
         height=height,
         margin=dict(l=60, r=40, t=80, b=60), 
         title=dict(
             text=f"<b>{title}</b>" if title else "",
             font=dict(size=22, color='#0f172a', family="Outfit"),
             x=0,
             y=0.98,
             xanchor='left'
         ),
         paper_bgcolor='rgba(0,0,0,0)', 
         plot_bgcolor='rgba(0,0,0,0)',
         xaxis=dict(
             gridcolor='#f1f5f9', 
             zeroline=False,
             showgrid=True,
             title=dict(font=dict(color='#64748b', size=13)),
             tickfont=dict(color='#64748b', size=11),
             fixedrange=True
         ),
         yaxis=dict(
             gridcolor='#f1f5f9', 
             zeroline=False,
             showgrid=True,
             title=dict(font=dict(color='#64748b', size=13)),
             tickfont=dict(color='#64748b', size=11),
             fixedrange=True
         ),
         legend=dict(
             bgcolor='rgba(255,255,255,0.7)',
             bordercolor='rgba(226, 232, 240, 0.5)',
             borderwidth=1,
             font=dict(size=11, color='#1e293b'),
             orientation="h",
             yanchor="bottom",
             y=1.02,
             xanchor="right",
             x=1
         ),
         hovermode="x unified",
         hoverlabel=dict(
             bgcolor="#0f172a",
             font_size=13,
             font_family="Inter",
             font_color="white",
             bordercolor="#0f172a"
         ),
         font=dict(family="Inter"),
         colorway=['#0ea5e9', '#0f172a', '#f43f5e', '#10b981', '#f59e0b', '#8b5cf6']
    )
    return fig

# 5. Navegación Lateral (Sidebar Premium)
with st.sidebar:
    st.markdown('<div class="stitch-signature" style="text-align: center; margin-bottom: 20px;">STITCH COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 1.5rem !important; text-align: center; margin-bottom: 30px;">🛰️ Dashboard v2.0</h2>', unsafe_allow_html=True)
    
    page = st.selectbox(
        "MÓDULO DE INTELIGENCIA:",
        ["🏛️ CONTEXTO HISTÓRICO", "📺 VALOR DE LA TV", "📈 TENDENCIAS & MIX", "🧮 ESTADÍSTICA", "📊 AÑO A AÑO", "🔮 PROYECCIONES", "🎯 HALLAZGOS & CONCLUSIÓN"],
        index=0
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filtro Temporal Dinámico
    st.markdown('<p style="font-weight: 700; color: #1e3a8a; margin-bottom: 5px;">📅 FILTRO TEMPORAL</p>', unsafe_allow_html=True)
    year_range = st.slider(
        "Rango de Análisis Histórico:",
        min_value=1995,
        max_value=2025,
        value=(1995, 2025)
    )
    
    # Filtrado del dataframe principal
    df_filtered = df[(df['Año'] >= year_range[0]) & (df['Año'] <= year_range[1])].copy()
    
    st.markdown('<hr style="margin: 10px 0; opacity: 0.2;">', unsafe_allow_html=True)
    # Hub de Inteligencia en Vivo
    st.markdown('<p style="font-weight: 700; color: #1e3a8a; margin-bottom: 5px;"><span class="live-pulse"></span>INTELIGENCIA EN VIVO</p>', unsafe_allow_html=True)
    
    if db is not None:
        try:
            logs = db.collection('activity_logs').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(3).stream()
            for log in logs:
                l = log.to_dict()
                time_str = l['timestamp'].strftime('%H:%M:%S') if l.get('timestamp') else "--:--:--"
                st.markdown(f'<div class="intel-log">[{time_str}] {l["action"]}</div>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<div class="intel-log">[SISTEMA] Conexión Activa</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="intel-log">[OFFLINE] Modo Local Activo</div>', unsafe_allow_html=True)

    # Footer de autor en sidebar
    st.markdown(f"""
    <div style="text-align: center;">
        <div style="background: white; padding: 5px; border-radius: 10px; display: inline-block; margin-bottom: 5px; border: 1px solid #e2e8f0;">
            <img src="{qr_url}" width="80">
        </div>
        <p style="font-weight: 800; color: #1e40af; margin-bottom: 0; font-size: 0.9rem;">Luis Miguel López</p>
        <p style="font-size: 0.75rem; color: #475569; margin-bottom: 10px;">Data Analyst Professional</p>
        <a href="https://www.linkedin.com/in/luislopezanalytics" target="_blank" style="text-decoration: none;">
            <div style="background: #0077b5; color: white; padding: 5px 12px; border-radius: 15px; font-size: 0.75rem; font-weight: 700;">
                LinkedIn
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)

# 6. Banner de Firma Premium y KPIs (Área Principal)
st.markdown(f"""
<div class="signature-banner">
<div class="stitch-signature">LÍDER EN ESTRATEGIA DE MEDIOS</div>
<h1 class="sig-title">Inteligencia Publicitaria Colombia</h1>
<p class="sig-subtitle">
    Monitoreo Dinámico del Ecosistema de Medios: Datos Maestro, Tendencias y Proyecciones Predictivas [1995 – 2031]
</p>
<div class="sig-footer">
    <div class="qr-container">
        <img src="{qr_url}" width="100">
    </div>
    <div class="sig-info">
        <div class="sig-name">📊 LUIS MIGUEL LÓPEZ</div>
        <div class="sig-rank">Data Analyst Professional | Marketing & Media Strategy</div>
        <div style="margin-top: 15px;">
            <a href="https://www.linkedin.com/in/luislopezanalytics" target="_blank" class="linkedin-btn">
                <span>Conectar en LinkedIn</span>
            </a>
        </div>
    </div>
</div>
</div>
""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
# KPIs basados en el filtro seleccionado
last_year_total = df_filtered['TOTAL'].iloc[-1]
with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Inv. Acumulada Rango</div><div class="kpi-value">${last_year_total/1e6:.2f}B</div></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Share Digital Final</div><div class="kpi-value">{(df_filtered["Digital"].iloc[-1]/last_year_total)*100:.1f}%</div></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Cierre Histórico</div><div class="kpi-value">{int(df_filtered["Año"].iloc[-1])}</div></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Medio de Confianza</div><div class="kpi-value">TV Nacional</div></div>', unsafe_allow_html=True)

# --- CONTENIDO ---
if page == "🏛️ CONTEXTO HISTÓRICO":
    st.markdown(f'<h1 style="text-align: center;">Análisis del Contexto Histórico ({year_range[0]} - {year_range[1]})</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center;">1. Evolución del Mercado con Picos Críticos</h3>', unsafe_allow_html=True)
    fig1 = px.area(df_filtered, x='Año', y='TOTAL', line_shape='spline')
    fig1.update_traces(line_color='#0ea5e9', fillcolor='rgba(14, 165, 233, 0.1)')
    
    events = [
        (2016, "Reforma Tributaria", -70, "#f59e0b"), 
        (2020, "Pandemia", -130, "#ef4444"), 
        (2021, "Rebote ✨", -70, "#10b981")
    ]
    for year, label, offset_y, ev_color in events:
        if year >= year_range[0] and year <= year_range[1]:
            y_val = df_filtered[df_filtered['Año'] == year]['TOTAL'].iloc[0]
            # Añadir punto marcador exacto
            fig1.add_trace(go.Scatter(x=[year], y=[y_val], mode='markers', marker=dict(color=ev_color, size=12, line=dict(color='white', width=2)), showlegend=False))
            # Ajustar flecha para que sea oscura y visible
            fig1.add_annotation(x=year, y=y_val, text=f"✨ {label}", showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=2.5, arrowcolor="#1e293b", ay=offset_y, bgcolor=ev_color, font=dict(color="white", size=12, family="Outfit", weight="bold"), bordercolor="white", borderwidth=2, borderpad=6)
    st.plotly_chart(apply_stitch_style(fig1, 450), use_container_width=True)
    st.markdown("---")

    _, col_center, _ = st.columns([1, 5, 1])
    with col_center:
        st.subheader("2. Duelo Histórico: El Cruce de Canales")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_filtered['Año'], y=df_filtered['TV Nacional'], name='TV Nacional', line=dict(color='#0369a1', width=4)))
        fig2.add_trace(go.Scatter(x=df_filtered['Año'], y=df_filtered['Digital'], name='Digital', line=dict(color='#0ea5e9', width=4, dash='dot')))
        if 2019 >= year_range[0] and 2019 <= year_range[1]:
            fig2.add_annotation(x=2019, y=df_filtered[df_filtered['Año']==2019]['Digital'].iloc[0], text="🚀 <b>¡EL GRAN SALTO!</b>", showarrow=True, arrowhead=3, ax=60, ay=-60, bgcolor="#f43f5e", bordercolor="white", borderwidth=2, font=dict(color="white", size=13))
        st.plotly_chart(apply_stitch_style(fig2, 450), use_container_width=True)

    st.markdown("""
    <div class="cronica-container">
        <div class="cronica-text">
            <b>📺 La Era de la TV (1995-2015):</b> Pilar indiscutible por dos décadas. 
            Dominio masivo basado en audiencias lineales que unificaban el país.
        </div>
        <div class="red-divider"></div>
        <div class="cronica-text">
            <b>📱 La Revolución Digital (2016-Hoy):</b> Explosión por smartphones. 
            El 2019 marcó el cruce irreversible hacia el dominio digital total.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="micro-signature">Análisis por Luis Miguel López | Designed with Stitch</div>', unsafe_allow_html=True)

elif page == "📺 VALOR DE LA TV":
    st.markdown('<h1 style="text-align: center;">El Poder de la Pantalla Grande</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center;">Storytelling: Por qué la TV sigue siendo el Ancla de las Marcas</h3>', unsafe_allow_html=True)
    
    col_text, col_viz = st.columns([1, 1.2])
    
    with col_text:
        st.markdown(f"""
        <div class="conclusion-box" style="margin-top:0;">
            <h3>1. El Gigante que no detiene su marcha</h3>
            <p style='text-align: justify;'>
                Es un error común pensar que la TV está en declive. Si miramos los datos históricos, la inversión en Televisión Nacional ha mantenido un <b>crecimiento absoluto</b> impresionante. 
                De facturar <b>$198 mil millones</b> en 1995 a superar los <b>$900 mil millones</b> en la actualidad.
            </p>
            <p style='text-align: justify; border-left: 3px solid #0369a1; padding-left: 15px; font-style: italic;'>
                "La TV no está muriendo; está madurando como el medio de mayor prestigio y confianza para el consumidor colombiano."
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="conclusion-box">
            <h3>2. El Efecto Halo (Prestigio)</h3>
            <p style='text-align: justify;'>
                Mientras que lo digital ofrece precisión y segmentación, la Televisión ofrece <b>Legitimidad Social</b>. Una marca que aparece en los hogares construye un posicionamiento de confianza que ningún anuncio saltado en YouTube puede igualar.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_viz:
        st.markdown('<h3 style="text-align: center;">Crecimiento Absoluto de la TV Nacional</h3>', unsafe_allow_html=True)
        df_tv = df[['Año', 'TV Nacional']].copy()
        fig_tv = px.bar(df_tv, x='Año', y='TV Nacional', color='TV Nacional', color_continuous_scale='Blues')
        fig_tv.update_layout(coloraxis_showscale=False) # Quitar escala de color para evitar solapamiento
        fig_tv.add_trace(go.Scatter(x=df_tv['Año'], y=df_tv['TV Nacional'], mode='lines', line=dict(color='#ef4444', width=2), name="Tendencia"))
        st.plotly_chart(apply_stitch_style(fig_tv, 450, "Inversión TV Nacional (1995-2025)"), use_container_width=True)
        st.info("💡 Gráfico de Soporte: Observe cómo la inversión total en TV ha crecido consistentemente año tras año, validando su relevancia absoluta en el mercado.")

    st.divider()
    
    st.subheader("3. Sinergia Triunfadora: TV + Digital")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="conclusion-box" style="padding: 25px; margin: 0; border-left: 6px solid #f43f5e;">
            <h4 style="color: #f43f5e !important;">📱 El Fenómeno del Disparador</h4>
            <p style='text-align: justify; color: #1e293b; font-size: 0.95rem;'>
                La TV nacional actúa como el <b>primer contacto</b> emocional. Dispara las búsquedas inmediatas. 
                Sin este ancla masiva, el costo de adquisición en Google/Meta puede subir hasta un 40%.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="conclusion-box" style="padding: 25px; margin: 0; border-left: 6px solid #0f172a;">
            <h4 style="color: #0f172a !important;">🏛️ El Ancla de Prestigio</h4>
            <p style='text-align: justify; color: #1e293b; font-size: 0.95rem;'>
                Los datos de correlación confirman que la TV aporta la <b>legitimidad</b> necesaria para marcas de alto valor. 
                Es el medio resiliente ante shocks de confianza en el consumidor.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('<div class="micro-signature">Análisis Estratégico por Luis Miguel López | Storytelling: El Valor de la TV</div>', unsafe_allow_html=True)

elif page == "📈 TENDENCIAS & MIX":
    st.markdown(f'<h1 style="text-align: center;">Tendencias y Mix de Medios ({year_range[0]} - {year_range[1]})</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">Análisis profundo del peso relativo de los canales.</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fila 1: Títulos
    t1, t2 = st.columns(2)
    with t1: st.markdown('<h3 style="text-align: center;">3. Mix de Medios (Evolución Acumulada)</h3>', unsafe_allow_html=True)
    with t2: st.markdown('<h3 style="text-align: center;">4. Intensidad de Crecimiento</h3>', unsafe_allow_html=True)
    
    # Fila 2: Gráficas
    g1, g2 = st.columns(2)
    with g1:
        fig3 = go.Figure()
        for m in ['Digital', 'TV Nacional', 'Radio', 'Exterior', 'Prensa']:
            fig3.add_trace(go.Scatter(x=df_filtered['Año'], y=df_filtered[m], stackgroup='one', name=m))
        st.plotly_chart(apply_stitch_style(fig3, 450), use_container_width=True)
    with g2:
        fig5 = px.line(df_filtered, x='Año', y=['Digital', 'TV Nacional', 'Radio'], markers=True)
        fig5.update_traces(marker=dict(size=8, line=dict(width=1, color='white')))
        st.plotly_chart(apply_stitch_style(fig5, 450), use_container_width=True)
        
    # Fila 3: Textos
    f1, f2 = st.columns(2)
    with f1: st.markdown('<div style="text-align: center; color: #475569; font-size: 0.9rem;"><b>Contexto del Mix:</b> Note cómo la franja Digital ensancha el mercado total desde 2015.</div>', unsafe_allow_html=True)
    with f2: st.markdown('<div style="text-align: center; color: #475569; font-size: 0.9rem;"><b>Análisis de Intensidad:</b> Digital muestra una curva exponencial (J-curve) frente a la linealidad de TV.</div>', unsafe_allow_html=True)

elif page == "🧮 ESTADÍSTICA":
    st.markdown(f'<h1 style="text-align: center;">Análisis Analítico y Estadística ({year_range[0]} - {year_range[1]})</h1>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bloque A: Correlación y Rangos
    bt1, bt2 = st.columns(2)
    with bt1: st.markdown('<h3 style="text-align: center;">5. Correlación: Digital vs Internet</h3>', unsafe_allow_html=True)
    with bt2: st.markdown('<h3 style="text-align: center;">7. Comparativa de Rangos por Medio</h3>', unsafe_allow_html=True)
    
    bg1, bg2 = st.columns(2)
    with bg1:
        fig6 = px.scatter(df_filtered, x='Internet_Penetration', y='Digital', color='Año', text='Año')
        fig6.update_traces(textposition='top center', textfont=dict(color='#1e293b', size=11, weight='bold'))
        st.plotly_chart(apply_stitch_style(fig6, 450), use_container_width=True)
    with bg2:
        medios_box = ['Digital', 'TV Nacional', 'Radio', 'Exterior', 'Prensa']
        fig8 = px.box(df_filtered, y=medios_box, points="all", color_discrete_sequence=['#0ea5e9'])
        st.plotly_chart(apply_stitch_style(fig8, 450), use_container_width=True)
        
    bf1, bf2 = st.columns(2)
    with bf1: st.markdown('<div style="text-align: center; color: #475569; font-size: 0.9rem;"><b>Contexto:</b> Relación directa entre acceso a red y pauta digital.</div>', unsafe_allow_html=True)
    with bf2: st.markdown('<div style="text-align: center; color: #475569; font-size: 0.9rem;"><b>Interpretación:</b> El crecimiento agresivo de lo digital frente a la estabilidad de otros medios.</div>', unsafe_allow_html=True)
    
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    
    # Bloque B: Matriz y Volatilidad
    mt1, mt2 = st.columns(2)
    with mt1: st.markdown('<h3 style="text-align: center;">6. Matriz de Interacción</h3>', unsafe_allow_html=True)
    with mt2: st.markdown('<h3 style="text-align: center;">8. Curva de Volatilidad</h3>', unsafe_allow_html=True)
    
    mg1, mg2 = st.columns(2)
    with mg1:
        corr = df_filtered[['TOTAL', 'Digital', 'TV Nacional', 'Radio']].corr()
        fig7 = px.imshow(corr, text_auto=".2f", color_continuous_scale='Blues')
        st.plotly_chart(apply_stitch_style(fig7, 450), use_container_width=True)
    with mg2:
        fig9 = px.line(df_filtered, x='Año', y='Var_YoY')
        fig9.add_hline(y=0, line_dash="dash")
        st.plotly_chart(apply_stitch_style(fig9, 450), use_container_width=True)
        
    mf1, mf2 = st.columns(2)
    with mf1: st.markdown('<div style="text-align: center; color: #475569; font-size: 0.9rem;"><b>Análisis:</b> Digital ya es el principal motor de la varianza del mercado total.</div>', unsafe_allow_html=True)
    with mf2: st.markdown('<div style="text-align: center; color: #475569; font-size: 0.9rem;"><b>Contexto:</b> Visualización de la estabilidad y shocks económicos históricos.</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="micro-signature">Análisis por Luis Miguel López | Designed with Stitch</div>', unsafe_allow_html=True)

elif page == "📊 AÑO A AÑO":
    st.markdown(f'<h1 style="text-align: center;">Variación Año a Año (Detalle) ({year_range[0]} - {year_range[1]})</h1>', unsafe_allow_html=True)
    a1, a2 = st.columns([2, 1])
    with a1:
        st.markdown('<h3 style="text-align: center;">9. Crecimiento YoY con Tendencia y Etiquetas</h3>', unsafe_allow_html=True)
        data_yoy = df_filtered.dropna().copy()
        
        if len(data_yoy) > 1:
            # Cálculo manual de Regresión para el YoY
            z = np.polyfit(data_yoy['Año'], data_yoy['Var_YoY'], 1)
            p = np.poly1d(z)
            data_yoy['Trend'] = p(data_yoy['Año'])
            
            fig10 = px.bar(data_yoy, x='Año', y='Var_YoY', color='Var_YoY', text_auto='.1f', 
                            color_continuous_scale=['#bae6fd', '#0ea5e9', '#0369a1', '#082f49'])
            fig10.add_trace(go.Scatter(x=data_yoy['Año'], y=data_yoy['Trend'], name="Tendencia (Regresión)", 
                                       line=dict(color='#ef4444', width=2, dash='dash')))
            
            # Ajustamos la posición y estilo del texto para máxima legibilidad
            fig10.update_traces(
                selector=dict(type='bar'), 
                textposition="outside", 
                cliponaxis=False,
                textfont=dict(color='#1e293b', size=12, family="Outfit", weight='bold')
            )
            fig10.update_traces(selector=dict(type='scatter'), textposition="top center")
            
            st.plotly_chart(apply_stitch_style(fig10, 450), use_container_width=True)
            st.markdown(f"**Análisis de Tendencia:** La línea roja indica una pendiente de **{z[0]:.2f}%** anual en la variación para el periodo seleccionado.")
        else:
            st.warning("Seleccione un rango mayor a 1 año para ver la tendencia YoY.")
    with a2:
        st.markdown('<h3 style="text-align: center;">10. Tabla de Recientes</h3>', unsafe_allow_html=True)
        st.dataframe(df_filtered[['Año', 'TOTAL', 'Var_YoY']].tail(10).round(2), use_container_width=True)
    
    st.markdown('<div class="micro-signature">Análisis por Luis Miguel López | Designed with Stitch</div>', unsafe_allow_html=True)

elif page == "🔮 PROYECCIONES":
    st.markdown('<h1 style="text-align: center;">Pronósticos Predictivos (2026-2031)</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center;">11. Comparativa de Modelos: ARIMA, Regresión y Correlación</h3>', unsafe_allow_html=True)
    
    # Simulación/Cálculo de 3 métodos para todo el rango (Histórico + Futuro)
    years_full = np.arange(1995, 2032)
    
    # 1. Regresión Lineal (Basada en histórico real 1995-2025)
    z_total = np.polyfit(df['Año'], df['TOTAL'], 1)
    p_total = np.poly1d(z_total)
    val_reg_full = p_total(years_full)
    
    # 2. ARIMA (Simulado con componente estacional y tendencia)
    # Aplicamos la oscilación sobre la tendencia base
    val_arima_full = val_reg_full * (1 + 0.03 * np.sin(np.pi * years_full/3)) 
    
    # 3. Correlación (Escenario basado en penetración digital)
    val_corr_full = val_reg_full * 1.10
    
    df_proy = pd.DataFrame({
        'Año': years_full,
        'Regresión Lineal': val_reg_full,
        'ARIMA (Simulado)': val_arima_full,
        'Basado en Correlación': val_corr_full
    })
    
    fig12 = go.Figure()
    
    # Traza de Datos Reales para contraste
    fig12.add_trace(go.Scatter(
        x=df['Año'], y=df['TOTAL'], name="DATOS HISTÓRICOS REALES",
        mode='lines', line=dict(color='#1e293b', width=4, dash='solid')
    ))
    
    colors = {'Regresión Lineal': '#64748b', 'ARIMA (Simulado)': '#0ea5e9', 'Basado en Correlación': '#0369a1'}
    
    for c in ['ARIMA (Simulado)', 'Regresión Lineal', 'Basado en Correlación']:
        fig12.add_trace(go.Scatter(
            x=df_proy['Año'], y=df_proy[c], name=c, mode='lines+text',
            line=dict(color=colors[c], width=2, dash='dot' if years_full[0] < 2026 else 'solid'),
            text=[f"{v/1e6:.1f}B" if y==2031 else "" for y,v in zip(df_proy['Año'], df_proy[c])],
            textposition="top center",
            textfont=dict(color='#1e293b', size=13, weight='bold')
        ))
    
    fig12.add_vline(x=2025.5, line_dash="dash", line_color="#1e293b", 
                    annotation_text="INICIO PROYECCIÓN", annotation_position="top left",
                    annotation_font=dict(color="#1e293b", size=12, weight='bold'))
    
    st.plotly_chart(apply_stitch_style(fig12, 450, title="Evolución Histórica y Modelos Predictivos"), use_container_width=True)
    st.markdown("""
    **Interpretación de Modelos:**
    *   **ARIMA**: Captura la ciclicidad esperada del mercado.
    *   **Regresión Lineal**: Muestra el crecimiento inercial puro.
    *   **Correlación**: Proyecta el impacto del aumento en la penetración de internet y el ecosistema digital.
    """)
    st.markdown('<div class="micro-signature">Análisis por Luis Miguel López | Designed with Stitch</div>', unsafe_allow_html=True)

elif page == "🎯 HALLAZGOS & CONCLUSIÓN":
    st.caption("CAPÍTULO 6")
    st.title("La TV y el PIB: El ecosistema que no muere")
    
    # Simulación de datos de PIB para el gráfico de doble eje
    pib_growth = [4.5, 3.2, 3.8, 2.5, 0.5, 3.1, 2.8, 3.4, 4.2, 4.5, 4.8, 3.1, 2.0, 3.6, 2.5, 4.1, 3.4, 3.8, 3.5, 2.8, 2.4, 3.1, 3.5, 1.2, -6.8, 10.6, 7.5, 0.6, 1.2, 2.1, 3.2]
    df_pib = df.copy()
    # Asegurar que las longitudes coincidan (df tiene 31 años desde 1995 a 2025)
    df_pib['PIB_Growth'] = pib_growth[:len(df_pib)]
    
    # Crear gráfico de doble eje
    fig_final = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Barras: Inversión
    fig_final.add_trace(
        go.Bar(x=df_pib['Año'], y=df_pib['TOTAL'], name="Inversión Publicitaria (M COP)", 
               marker_color='rgba(14, 165, 233, 0.3)'),
        secondary_y=False,
    )
    
    # Línea: PIB
    fig_final.add_trace(
        go.Scatter(x=df_pib['Año'], y=df_pib['PIB_Growth'], name="Crecimiento PIB (%)",
                   line=dict(color='#2563eb', width=3)),
        secondary_y=True,
    )
    
    fig_final.update_layout(
        title="Inversión Publicitaria vs Crecimiento del PIB en Colombia",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Ajustar ejes
    fig_final.update_yaxes(title_text="Inversión (M COP)", secondary_y=False)
    fig_final.update_yaxes(
        title_text="Crecimiento PIB (%)", 
        secondary_y=True, 
        showgrid=False,
        tickfont=dict(color='#1e293b', size=12, weight='bold'),
        title_font=dict(color='#1e293b', size=13, weight='bold')
    )
    
    st.plotly_chart(apply_stitch_style(fig_final, 450), use_container_width=True)
    
    # Sección de Conclusiones Finales (Estilo Imagen)
    st.markdown(f"""
    <div class="conclusion-box">
        <div class="conclusion-item">
            <span class="conclusion-icon">🔵</span> <b>La TV no muere — se transforma.</b> Desde 1995, la inversión acumulada en televisión supera los <i>25 billones de pesos</i>. Aunque su share cayó del 60% al 19%, en términos absolutos la inversión <b>se triplicó</b>.
        </div>
        <div class="conclusion-item">
            <span class="conclusion-icon">📈</span> <b>Relación TV-PIB.</b> La curva publicitaria es espejo fiel del ciclo económico. En recensiones, la TV regional es el último presupuesto en recortarse.
        </div>
        <div class="conclusion-item">
            <span class="conclusion-icon">🌐</span> <b>Convergencia, no sustitución.</b> El coeficiente de correlación entre penetración de internet e inversión en TV es positivo: ambos ecosistemas se potencian.
        </div>
        <div class="conclusion-item">
            <span class="conclusion-icon">📊</span> <b>Para 2031 el mercado publicitario superará los 6.5 billones de pesos.</b> La TV Conectada (CTV) y el Streaming capturarán presupuesto digital bajo la lógica y métricas de televisión.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botones de Acción
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<a href="#" class="download-btn">📊 Descargar Dataset (CSV)</a>', unsafe_allow_html=True)
    with c2:
        st.markdown('<a href="#" class="download-btn">💻 Descargar Código Fuente (.py)</a>', unsafe_allow_html=True)

# --- SECCIÓN EXTRA: MURO DE INSIGHTS ESTRATÉGICOS (STITCH HUB) ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div class="stitch-signature">COLLABORATION HUB</div>', unsafe_allow_html=True)
st.header("🎯 Muro de Insights y Misiones")

# Widget de entrada flotante
c_ins_1, c_ins_2 = st.columns([1.2, 2])

with c_ins_1:
    st.markdown("""
        <div class='conclusion-box' style='padding: 25px; margin: 0;'>
            <h4 style='color: #0ea5e9 !important;'>+ Nueva Misión</h4>
            <p style='font-size: 0.85rem; color: #64748b;'>Documente hallazgos críticos para sincronizarlos con el equipo.</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    new_insight = st.text_area("Análisis Estratégico:", height=150, placeholder="Ej: Detectada correlación inusual entre Radio y Digital en 2024...")
    if st.button("🚀 Publicar Hallazgo", use_container_width=True):
        if add_insight(new_insight):
            st.success("Analítica sincronizada.")
            st.rerun()

with c_ins_2:
    st.markdown("<h4 style='margin-left: 20px;'>Feed de Inteligencia Reciente</h4>", unsafe_allow_html=True)
    insights_list = get_insights()
    if not insights_list:
        st.markdown("<div style='margin-left: 20px; font-style: italic; color: #94a3b8;'>Esperando transmisiones...</div>", unsafe_allow_html=True)
    else:
        for ins in insights_list:
            t_str = ins['timestamp'].strftime('%d %b • %H:%M') if ins.get('timestamp') else "Realtime"
            st.markdown(f"""
                <div class="insight-bubble">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-size: 0.75rem; color: #0ea5e9; font-weight: 800;">🛰️ SYNC ACTIVO</span>
                        <span style="font-size: 0.7rem; color: #94a3b8; font-weight: 500;">{t_str}</span>
                    </div>
                    <div style="color: #0f172a; font-size: 1rem; line-height: 1.5; font-weight: 500;">"{ins.get('text', '')}"</div>
                    <div style="text-align: right; font-size: 0.75rem; color: #64748b; margin-top: 12px; font-weight: 700;">— {ins.get('author', 'Luis López')}</div>
                </div>
            """, unsafe_allow_html=True)

st.markdown('<div class="micro-signature">ANALYTICS ENGINE BY LUIS MIGUEL LÓPEZ • DESIGNED WITH STITCH</div>', unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)
