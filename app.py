import streamlit as st
import datetime
from modules import protocols, bio_math, pdf_engine, vision_ai
import google.generativeai as genai

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="AREA 199 | LAB", layout="wide", page_icon="🔴")

# --- CSS AREA 199 ---
st.markdown("""
<style>
    .stApp {background-color: #000000; color: #ffffff;}
    h1, h2, h3 {color: #E20613 !important; text-transform: uppercase;}
    .stButton>button {border: 2px solid #E20613; color: #E20613; background: transparent; width: 100%; font-weight: bold;}
    .stButton>button:hover {background: #E20613; color: white;}
    .metric-box {border-left: 4px solid #E20613; background: #111; padding: 15px; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# --- SESSIONE ---
if 'paziente' not in st.session_state:
    st.session_state.paziente = {
        "anagrafica": {"data": datetime.date.today()},
        "misure": {"Cav": 84.0, "T": 60.0, "B": 65.0},
        "geometrie": {},
        "discipline": "Road"
    }

# --- SIDEBAR ---
with st.sidebar:
    st.header("AREA 199")
    st.divider()
    page = st.radio("NAVIGAZIONE", ["DASHBOARD CLINICA", "BIOMECCANICA", "REPORT"])
    st.divider()
    
    # SELETTORE DISCIPLINA
    st.markdown("### 🚴 DISCIPLINA")
    disc = st.selectbox("Seleziona Tipo Bici", ["Road", "MTB", "Gravel", "TT"])
    st.session_state.paziente['discipline'] = disc

# --- PAGINA 1: CLINICA ---
if page == "DASHBOARD CLINICA":
    st.title("CLINICAL DASHBOARD & TRIAGE")
    
    ana = st.session_state.paziente['anagrafica']
    c1, c2 = st.columns(2)
    ana['nome'] = c1.text_input("Nome Atleta")
    ana['cognome'] = c2.text_input("Cognome Atleta")
    
    st.subheader("ANAMNESI E SINTOMI")
    sintomi = st.text_area("Descrivi dolore o obiettivi:", height=150)
    
    if st.button("🧠 ANALISI AI (AREA BRAIN)"):
        # Qui usiamo st.secrets per la sicurezza
        if "gemini_key" in st.secrets:
            genai.configure(api_key=st.secrets["gemini_key"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"{protocols.SYS_TRIAGE}\n\nSINTOMI: {sintomi}")
            st.markdown(f"<div class='metric-box'>{response.text}</div>", unsafe_allow_html=True)
            st.session_state.paziente['relazione_ai'] = response.text
        else:
            st.error("Chiave API Mancante nei Secrets!")

# --- PAGINA 2: BIOMECCANICA ---
elif page == "BIOMECCANICA":
    disc = st.session_state.paziente['discipline']
    st.title(f"LAB BIOMECCANICO: {disc}")
    
    col_input, col_out = st.columns([1, 2])
    
    with col_input:
        st.subheader("MISURE (cm)")
        m = st.session_state.paziente['misure']
        m['Cav'] = st.number_input("Cavallo", value=m['Cav'])
        m['T'] = st.number_input("Tronco", value=m['T'])
        m['B'] = st.number_input("Braccio", value=m['B'])
        
        if st.button("CALCOLA ASSETTO"):
            # CHIAMA IL NUOVO MODULO MULTI-DISCIPLINA
            geo = bio_math.calcola_assetto_multidisciplina(disc, m['Cav'], m['T'], m['B'])
            st.session_state.paziente['geometrie'] = geo
            
    with col_out:
        if st.session_state.paziente['geometrie']:
            geo = st.session_state.paziente['geometrie']
            st.subheader("GEOMETRIE TARGET")
            
            c1, c2 = st.columns(2)
            c1.markdown(f"<div class='metric-box'><h3>ALTEZZA SELLA</h3><h1>{geo['AS']} cm</h1></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-box'><h3>DIST. SELLA-MAN</h3><h1>{geo['SY']} cm</h1></div>", unsafe_allow_html=True)
            
            c3, c4 = st.columns(2)
            c3.info(f"ARRETRAMENTO: {geo['SK']} cm")
            c4.warning(f"DROP (SCARTO): {geo['KW']} cm")
            
            st.caption(f"Calcolo specifico per disciplina: {disc}. Stem suggerito: {geo['Stem']}mm.")

# --- PAGINA 3: REPORT ---
elif page == "REPORT":
    st.title("ESPORTAZIONE PDF")
    if st.button("📄 GENERA DOCUMENTO PDF"):
        pdf_data = pdf_engine.genera_report(st.session_state.paziente, st.session_state.paziente['discipline'])
        st.download_button("SCARICA PDF", data=pdf_data, file_name="Report_Area199.pdf", mime="application/pdf")
