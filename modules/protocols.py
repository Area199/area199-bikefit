# ==============================================================================
# 🧠 DATABASE CLINICO ATS & TRIAGE
# ==============================================================================

PROTOCOLLI_MASTER = """
MANUALE OPERATIVO ATS - RIATLETIZZAZIONE & PREVENZIONE

PRINCIPI GENERALI TRASVERSALI:
1. Mai lavorare sul dolore acuto (>3/10 VAS).
2. Recupero funzionale: Catena Cinetica Chiusa prima di Aperta.
3. Metabolico: Usare SOLO %FTP (Power), mai zone cardio.

---
1. CERVICALE (MECCANOPATICA 98% / PATOMECCANICA)
FASE 1: POWER ATTENUATION (4-6 Settimane) - Isometria, Rivascolarizzazione.
FASE 2: POWER AMPLIFICATION (4-6 Settimane) - Stiffness, Ipertrofia funzionale.
FASE 3: ENERGY CONSERVATION (4-6 Settimane) - Speed, Power, Agility.

---
2. SPALLA (OVERHEAD ATHLETE)
FASE 1: ATTIVAZIONE (Dentato Anteriore).
FASE 2: INTEGRAZIONE GLOBALE (Catene cinetiche).
FASE 3: PERFORMANCE (Esplosività).

---
3. LOMBARE
PROTOCOLLO A (MECCANOPATICA): Mobilità Psoas, Core Flex.
PROTOCOLLO B (PATOMECCANICA): Sensibilità pelvica, Core Instabile.
"""

# DATABASE TEST
DB_TEST = {
    "CERVICALE": {
        "Test Mobilità Attiva": "Flessione, Estensione, Rotazione, Inclinazione.",
        "Chin Tuck": "Controllo motorio flessori profondi."
    },
    "SPALLA": {
        "Jobe Test": "Valutazione Sovraspinato.",
        "GIRD": "Deficit rotazione interna gleno-omerale."
    },
    "LOMBARE": {
        "Finger Floor Test": "Retrazione catena posteriore.",
        "Thomas Test": "Retrazione Ileopsoas/Retto femorale."
    }
}

# PROMPT SISTEMA PER L'AI
SYS_TRIAGE = f"""
Sei 'AREA BRAIN', esperto diagnostico del Lab Area 199.
ANALIZZA: Sintomi riferiti dall'atleta.
CONSULTA IL PROTOCOLLO MASTER ATS:
{PROTOCOLLI_MASTER}

OUTPUT RICHIESTO:
**SOSPETTO CLINICO:** [Ipotesi]
**FASE SUGGERITA:** [Fase 1/2/3]
**TEST DA ESEGUIRE:** [Scegli dal database]
"""

SYS_FINAL_REPORT = f"""
Sei il Responsabile Scientifico 'AREA 199'.
Scrivi la RELAZIONE TECNICA CONCLUSIVA per il report PDF.
Usa linguaggio medico-sportivo formale.
Includi: Inquadramento problema, Analisi Test, Strategia Intervento (Fasi ATS).
"""
