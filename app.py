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
    .success-box {border-left: 4px solid #4CAF50; background-color: #111; padding: 15px;}
    .error-box {border-left: 4px solid #f44336; background-color: #111; padding: 15px;}
</style>
""", unsafe_allow_html=True)

# --- INIZIALIZZA MEMORIA (SESSION STATE) ---
if 'analisi_fatta' not in st.session_state:
    st.session_state['analisi_fatta'] = False
if 'dati_video' not in st.session_state:
    st.session_state['dati_video'] = {}

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo_dark.jpg"):
        st.image("logo_dark.jpg", use_container_width=True)
    else:
        st.header("AREA 199")
    st.divider()
    st.info("Bikefit System V1.0")
    
    # Tasto Reset
    if st.button("🔄 NUOVA ANALISI"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

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
        
        # Bottone di avvio
        if st.button("🚀 AVVIA ANALISI AUTOMATICA"):
            with st.spinner("Calcolo angoli in corso... attendere..."):
                try:
                    video_out, max_ext, min_flex = vision_ai.processa_video(tfile.name)
                    
                    # SALVA IN MEMORIA PER NON FARLO SPARIRE
                    st.session_state['dati_video'] = {
                        'video_out': video_out,
                        'max_ext': max_ext,
                        'min_flex': min_flex
                    }
                    st.session_state['analisi_fatta'] = True
                    st.rerun() # Ricarica la pagina per mostrare i dati fissi
                except Exception as e:
                    st.error(f"Errore durante l'analisi: {e}")

        # SE L'ANALISI È GIÀ STATA FATTA, MOSTRA I DATI DALLA MEMORIA
        if st.session_state['analisi_fatta']:
            dati = st.session_state['dati_video']
            
            # Visualizzazione Metrica
            st.markdown(f"""
            <div class="metric-box">
                <h3>ESTENSIONE GINOCCHIO</h3>
                <h1 style="font-size: 4em; margin: 0;">{int(dati['max_ext'])}°</h1>
                <p style="color: #aaa;">Range Ottimale: 138° - 145°</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Diagnosi
            ext = dati['max_ext']
            if ext < 138:
                st.markdown(f"<div class='error-box'>⚠️ <b>SELLA BASSA</b><br>Alzare di circa <b>{int((142-ext)*1.5)} mm</b></div>", unsafe_allow_html=True)
            elif ext > 146:
                st.markdown(f"<div class='error-box'>⚠️ <b>SELLA ALTA</b><br>Abbassare di circa <b>{int((ext-142)*1.5)} mm</b></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='success-box'>✅ <b>POSIZIONE CORRETTA</b></div>", unsafe_allow_html=True)
            
            st.write("") # Spazio
            st.write("Video Elaborato con Scheletro:")
            st.video(dati['video_out'])

elif st.session_state['analisi_fatta']:
    # Se l'utente rimuove il file ma c'è ancora roba in memoria, pulisci
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()
