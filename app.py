import streamlit as st
import os
import tempfile
from modules import vision_ai

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="AREA 199 | BIKEFIT", layout="wide", page_icon="🔴")

st.markdown("""
<style>
    .stApp {background-color: #000000; color: #ffffff;}
    h1, h2, h3 {color: #E20613 !important; text-transform: uppercase; font-weight: 800;}
    .stButton>button {border: 2px solid #E20613; color: #E20613; background: transparent; font-weight: bold; width: 100%;}
    .stButton>button:hover {background: #E20613; color: white;}
    .metric-box {border-left: 4px solid #E20613; background-color: #111; padding: 10px; margin-bottom: 5px;}
    .big-num {font-size: 2.5em; font-weight: bold; color: white;}
    .sub-text {color: #aaa; font-size: 0.9em;}
</style>
""", unsafe_allow_html=True)

# Memoria
if 'dati_video' not in st.session_state: st.session_state['dati_video'] = None

with st.sidebar:
    if os.path.exists("logo_dark.jpg"): st.image("logo_dark.jpg", use_container_width=True)
    else: st.header("AREA 199")
    st.divider()
    if st.button("🔄 RESET"):
        st.session_state['dati_video'] = None
        st.rerun()

st.title("BIKEFIT LAB | TOTAL BODY AI")

uploaded_file = st.file_uploader("📂 CARICA VIDEO (LATO SINISTRO)", type=["mp4", "mov"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False) 
    tfile.write(uploaded_file.read())
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("1. VIDEO ORIGINALE")
        st.video(uploaded_file)
    
    with col2:
        st.subheader("2. ANALISI BIOMECCANICA")
        if st.button("🚀 AVVIA ANALISI COMPLETA"):
            with st.spinner("Analisi articolare completa..."):
                video_out, dati = vision_ai.processa_video(tfile.name)
                st.session_state['dati_video'] = {'video': video_out, 'stats': dati}
                st.rerun()

        # VISUALIZZAZIONE RISULTATI
        if st.session_state['dati_video']:
            res = st.session_state['dati_video']['stats']
            
            # LAYOUT A 3 COLONNE
            c1, c2, c3 = st.columns(3)
            
            # 1. GINOCCHIO
            with c1:
                st.markdown(f"""
                <div class="metric-box">
                    <div>GINOCCHIO (Max Ext)</div>
                    <div class="big-num">{int(res['max_knee'])}°</div>
                    <div class="sub-text">Target: 138°-145°</div>
                </div>
                """, unsafe_allow_html=True)
                if res['max_knee'] < 138: st.error("⚠️ ALZARE SELLA")
                elif res['max_knee'] > 146: st.error("⚠️ ABBASSARE SELLA")
                else: st.success("✅ SELLA OK")

            # 2. ANCA (BUSTO)
            with c2:
                st.markdown(f"""
                <div class="metric-box">
                    <div>ANCA (Flessione)</div>
                    <div class="big-num">{int(res['avg_hip'])}°</div>
                    <div class="sub-text">Chiusura busto</div>
                </div>
                """, unsafe_allow_html=True)
                if res['avg_hip'] < 45: st.warning("⚠️ BUSTO TROPPO CHIUSO")
                else: st.success("✅ ANCA OK")

            # 3. GOMITO
            with c3:
                st.markdown(f"""
                <div class="metric-box">
                    <div>GOMITO (Avg)</div>
                    <div class="big-num">{int(res['avg_arm'])}°</div>
                    <div class="sub-text">Target: 150°-160°</div>
                </div>
                """, unsafe_allow_html=True)
                if res['avg_arm'] > 170: st.warning("⚠️ BRACCIA TESE")
                else: st.success("✅ REACH OK")

            st.markdown("### 🎥 VIDEO ELABORATO (SCHELETRO ATTIVO)")
            st.video(st.session_state['dati_video']['video'])
