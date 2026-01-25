import streamlit as st
import os
import tempfile
from modules import vision_ai

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="AREA 199 | BIKEFIT", layout="wide", page_icon="🔴")

# --- STILE CSS ---
st.markdown("""
<style>
    .stApp {background-color: #000000; color: #ffffff;}
    h1, h2, h3 {color: #E20613 !important; text-transform: uppercase; font-weight: 800;}
    .stButton>button {border: 2px solid #E20613; color: #E20613; background: transparent; font-weight: bold; width: 100%;}
    .stButton>button:hover {background: #E20613; color: white;}
    .metric-box {border-left: 4px solid #E20613; background-color: #111; padding: 15px; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo_dark.jpg"):
        st.image("logo_dark.jpg", use_container_width=True)
    else:
        st.header("AREA 199")
    st.divider()
    st.info("Bikefit System V1.0")

# --- APP ---
st.title("BIKEFIT LAB | MOTION CAPTURE AI")

uploaded_file = st.file_uploader("📂 CARICA VIDEO PEDALATA LATERALE", type=["mp4", "mov"])

if uploaded_file is not None:
    # Salva file temporaneo
    tfile = tempfile.NamedTemporaryFile(delete=False) 
    tfile.write(uploaded_file.read())
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("1. VIDEO ORIGINALE")
        st.video(uploaded_file)
    
    with col2:
        st.subheader("2. ANALISI AI")
        if st.button("🚀 AVVIA ANALISI AUTOMATICA"):
            with st.spinner("Calcolo angoli in corso..."):
                video_out, max_ext, min_flex = vision_ai.processa_video(tfile.name)
                
                # Visualizzazione
                st.markdown(f"""
                <div class="metric-box">
                    <h3>ESTENSIONE GINOCCHIO</h3>
                    <h1 style="font-size: 3em;">{int(max_ext)}°</h1>
                    <p style="color: #aaa;">Range Ottimale: 138° - 145°</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Diagnosi
                if max_ext < 138: st.error("⚠️ SELLA BASSA: Alzare di ~5mm")
                elif max_ext > 146: st.error("⚠️ SELLA ALTA: Abbassare di ~3mm")
                else: st.success("✅ POSIZIONE CORRETTA")
                
                st.video(video_out)
