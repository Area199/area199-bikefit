import streamlit as st
import datetime
import os
import google.generativeai as genai
from modules import protocols, bio_math, pdf_engine, vision_ai

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="AREA 199 | LAB SYSTEM", layout="wide", page_icon="🔴")

# --- CSS AREA 199 ---
st.markdown("""
<style>
    .stApp {background-color: #000000; color: #ffffff;}
    h1, h2, h3 {color: #E20613 !important; text-transform: uppercase; font-family: sans-serif; font-weight: 800;}
    .stTextInput input, .stNumberInput input, .stSelectbox, .stMultiSelect, .stTextArea textarea {
        background-color: #1c1c1c !important; color: white !important; border: 1px solid #333 !important;
    }
    .stButton>button {
        background-color: transparent; color: #E20613; border: 2px solid #E20613; 
        font-weight: bold; border-radius: 0px; width: 100%; transition: all 0.3s;
    }
    .stButton>button:hover {background-color: #E20613; color: white;}
    .metric-box {border-left: 4px solid #E20613; background-color: #111; padding: 15px; margin-bottom: 10px;}
    .info-box { background-color: #111; border: 1px solid #444; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
    .info-title { color: #E20613; font-weight: bold; font-size: 16px; text-transform: uppercase; margin-bottom: 5px; }
    .success-box {border-left: 4px solid #4CAF50; background-color: #111; padding: 15px;}
    .error-box {border-left: 4px solid #f44336; background-color: #111; padding: 15px;}
</style>
""", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE SESSIONE ---
if 'paziente' not in st.session_state:
    st.session_state.paziente = {
        "step_corrente": "Dashboard",
        "anagrafica": {"data": datetime.date.today()}, 
        "misure": {"Cav": 84.0, "T": 60.0, "B": 65.0, "S": 40.0, "C": 40.0, "G": 40.0, "P": 26.0},
        "sella_dati": {"dit": 130.0, "dc_sx": 115.0, "dc_dx": 115.0, "code": "L1"},
        "sella_config": {},
        "geometrie_finali": {},
        "tacchette": {"dist_sx": 0, "rot_sx": 0, "dist_dx": 0, "rot_dx": 0},
        "discipline": "Road",
        "triage_ai": "",
        "relazione_finale_ai": "",
        "test_corrente": None,
        "risultati_test": {}
    }
# Memoria Video AI
if 'dati_video' not in st.session_state: st.session_state['dati_video'] = None

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo_dark.jpg"): st.image("logo_dark.jpg", use_container_width=True)
    else: st.header("AREA 199")
    st.divider()
    
    # NAVIGAZIONE
    page = st.radio("SEZIONE", ["DASHBOARD CLINICA", "BIOMECCANICA", "MOTION CAPTURE AI", "REPORT"])
    st.divider()
    
    # SELETTORE DISCIPLINA
    if page == "BIOMECCANICA":
        st.markdown("### 🚴 DISCIPLINA")
        disc = st.selectbox("Tipo Bici", ["Road", "MTB", "Gravel", "TT"])
        st.session_state.paziente['discipline'] = disc

# --- PAGINA 1: DASHBOARD CLINICA ---
if page == "DASHBOARD CLINICA":
    
    # GESTIONE SINGOLO TEST (SUB-ROUTINE)
    if st.session_state.paziente.get('test_corrente'):
        t_name = st.session_state.paziente['test_corrente']
        # Recupera info dal modulo protocols
        t_info = {}
        for area in protocols.DB_TEST.values(): # Cerca nel DB del modulo
             if t_name in area: t_info = area[t_name] # Adatta se la struttura è diversa, o usa dizionario piatto
        
        # Fallback se non trova nel DB semplificato
        desc = "Eseguire il test secondo protocollo ATS."
        
        st.title(f"ESECUZIONE: {t_name}")
        st.button("🔙 TORNA ALLA DIAGNOSI", on_click=lambda: st.session_state.paziente.update({'test_corrente': None}))
        
        st.markdown(f"""
        <div class="info-box">
            <div class="info-title">📋 PROCEDURA TECNICA</div>
            <div class="info-text">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        
        prev = st.session_state.paziente['risultati_test'].get(t_name, {}).get('esito', '')
        res = st.text_area("RISULTATI", value=prev, height=100)
        
        if st.button("SALVA ESITO"):
            st.session_state.paziente['risultati_test'][t_name] = {'esito': res}
            st.success("Dato salvato.")
            
    else:
        st.title("CLINICAL DASHBOARD & TRIAGE")
        ana = st.session_state.paziente['anagrafica']
        c1, c2 = st.columns(2)
        ana['nome'] = c1.text_input("Nome", ana.get('nome',''))
        ana['cognome'] = c2.text_input("Cognome", ana.get('cognome',''))
        
        st.subheader("ANAMNESI")
        sintomi = st.text_area("Descrizione Sintomi / Obiettivi", height=100, value=ana.get('storia',''))
        ana['storia'] = sintomi

        if st.button("🧠 ANALISI TRIAGE (AI)"):
             # Gestione Sicura Chiavi
             if "gemini_key" in st.secrets:
                 try:
                     genai.configure(api_key=st.secrets["gemini_key"])
                     model = genai.GenerativeModel('gemini-1.5-flash')
                     response = model.generate_content(f"{protocols.SYS_TRIAGE}\n\nSINTOMI: {sintomi}")
                     st.session_state.paziente['triage_ai'] = response.text
                 except Exception as e:
                     st.error(f"Errore AI: {e}")
             else:
                 st.warning("Chiave AI non configurata nei Secrets.")

        if st.session_state.paziente['triage_ai']:
            st.markdown(f"<div class='metric-box'>{st.session_state.paziente['triage_ai']}</div>", unsafe_allow_html=True)
            
        st.markdown("---")
        st.caption("PROTOCOLLI TEST DISPONIBILI")
        # Mostra i bottoni per i test dal modulo protocols
        for area, tests in protocols.DB_TEST.items():
            with st.expander(area):
                for t_name in tests:
                    if st.button(f"👉 {t_name}", key=t_name):
                        st.session_state.paziente['test_corrente'] = t_name
                        st.rerun()

# --- PAGINA 2: BIOMECCANICA ---
elif page == "BIOMECCANICA":
    disc = st.session_state.paziente['discipline']
    st.title(f"LAB BIOMECCANICO: {disc}")
    
    # 1. MISURE ANTROPOMETRICHE
    col_img, col_dati = st.columns([1, 2])
    with col_img:
        if os.path.exists("misure_antropometriche.jpg"): 
            st.image("misure_antropometriche.jpg", use_container_width=True)
    
    with col_dati:
        m = st.session_state.paziente['misure']
        c1, c2 = st.columns(2)
        m['Cav'] = c1.number_input("Cavallo", value=m['Cav'])
        m['T'] = c2.number_input("Tronco", value=m['T'])
        m['B'] = c1.number_input("Braccio", value=m['B'])
        m['S'] = c2.number_input("Spalle", value=m['S'])
        
        if st.button("CALCOLA ASSETTO TARGET"):
            # Chiama il modulo matematico avanzato
            geo = bio_math.calcola_assetto_multidisciplina(disc, m['Cav'], m['T'], m['B'])
            st.session_state.paziente['geometrie_finali'] = geo
            st.success("Calcolo Eseguito")

    # 2. RISULTATI GEOMETRIE
    if st.session_state.paziente['geometrie_finali']:
        geo = st.session_state.paziente['geometrie_finali']
        st.markdown("---")
        col_res, col_bike = st.columns([1, 1])
        
        with col_res:
            st.subheader("SETUP TARGET")
            st.markdown(f"<div class='metric-box'><h3>ALTEZZA SELLA</h3><h1>{geo['AS']} cm</h1></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>DIST. SELLA-MAN</h3><h1>{geo['SY']} cm</h1></div>", unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            c3.info(f"ARRETRAMENTO: {geo['SK']} cm")
            c4.warning(f"DROP: {geo['KW']} cm")
            
        with col_bike:
            if os.path.exists("geometrie_bdc.jpg"):
                st.image("geometrie_bdc.jpg", caption="Schema Riferimento", use_container_width=True)

# --- PAGINA 3: MOTION CAPTURE AI ---
elif page == "MOTION CAPTURE AI":
    st.title("ANALISI VIDEO AUTOMATICA")
    
    uploaded_file = st.file_uploader("📂 CARICA VIDEO PEDALATA (Lato SX)", type=["mp4", "mov"])
    
    if uploaded_file:
        import tempfile
        tfile = tempfile.NamedTemporaryFile(delete=False) 
        tfile.write(uploaded_file.read())
        
        col1, col2 = st.columns(2)
        with col1:
            st.video(uploaded_file)
        with col2:
            if st.button("🚀 AVVIA ANALISI"):
                with st.spinner("Elaborazione AI in corso..."):
                    video_out, dati = vision_ai.processa_video(tfile.name)
                    st.session_state['dati_video'] = {'video': video_out, 'stats': dati}
                    st.rerun()
                    
        if st.session_state['dati_video']:
            res = st.session_state['dati_video']['stats']
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.markdown(f"<div class='metric-box'><div>GINOCCHIO (Max)</div><h1>{int(res['max_knee'])}°</h1></div>", unsafe_allow_html=True)
                if res['max_knee'] < 138: st.error("SELLA BASSA")
                elif res['max_knee'] > 146: st.error("SELLA ALTA")
                else: st.success("OK")
                
            with c2:
                st.markdown(f"<div class='metric-box'><div>ANCA (Avg)</div><h1>{int(res['avg_hip'])}°</h1></div>", unsafe_allow_html=True)
            
            with c3:
                st.markdown(f"<div class='metric-box'><div>GOMITO (Avg)</div><h1>{int(res['avg_arm'])}°</h1></div>", unsafe_allow_html=True)
                
            st.video(st.session_state['dati_video']['video'])

# --- PAGINA 4: REPORT ---
elif page == "REPORT":
    st.title("ESPORTAZIONE REPORT")
    if st.button("📄 GENERA PDF AREA 199"):
        pdf_bytes = pdf_engine.genera_report(st.session_state.paziente, st.session_state.paziente['discipline'])
        st.download_button("📥 SCARICA PDF", data=pdf_bytes, file_name=f"Report_{st.session_state.paziente['anagrafica'].get('cognome','Area199')}.pdf", mime="application/pdf")
