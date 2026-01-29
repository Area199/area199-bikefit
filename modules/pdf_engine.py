from fpdf import FPDF
import os

class Area199PDF(FPDF):
    def header(self):
        # Logo Check
        if os.path.exists('logo_dark.jpg'): 
            self.image('logo_dark.jpg', 10, 8, 30)
        
        self.set_font('Arial', 'B', 16)
        self.cell(0, 8, 'AREA 199 PERFORMANCE LAB', 0, 1, 'R')
        self.set_font('Arial', 'B', 10)
        self.set_text_color(226, 6, 19) # Rosso AREA199
        self.cell(0, 5, 'METODO PETRUZZI - CLINICAL REPORT', 0, 1, 'R')
        self.ln(10)
        self.set_draw_color(226, 6, 19)
        self.line(10, 28, 200, 28)
        self.ln(5)

    def section_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(200, 0, 0)
        self.cell(0, 8, f"  {label}", 0, 1, 'L', 1)
        self.ln(3)

def genera_report(paziente, disciplina):
    pdf = Area199PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # DATI
    ana = paziente['anagrafica']
    geo = paziente['geometrie']
    
    # 1. ANAGRAFICA
    pdf.section_title(f"1. DATI ATLETA & DISCIPLINA: {disciplina.upper()}")
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Atleta: {ana.get('nome','')} {ana.get('cognome','')}", 0, 1)
    
    # 2. SETUP CALCOLATO
    pdf.ln(5)
    pdf.section_title("2. SETUP BIOMECCANICO TARGET")
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "PARAMETRO", 1)
    pdf.cell(40, 8, "VALORE", 1, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(40, 8, "Altezza Sella (AS)", 1)
    pdf.cell(40, 8, f"{geo.get('AS')} cm", 1, 1)
    
    pdf.cell(40, 8, "Arretramento (SK)", 1)
    pdf.cell(40, 8, f"{geo.get('SK')} cm", 1, 1)
    
    pdf.cell(40, 8, "Distanza Sella-Man", 1)
    pdf.cell(40, 8, f"{geo.get('SY')} cm", 1, 1)
    
    pdf.cell(40, 8, "Scarto (Drop)", 1)
    pdf.cell(40, 8, f"{geo.get('KW')} cm", 1, 1)

    # 3. AI REPORT
    pdf.ln(5)
    pdf.section_title("3. VALUTAZIONE AREA BRAIN")
    if 'relazione_ai' in paziente:
        pdf.set_font('Times', '', 11)
        pdf.multi_cell(0, 6, paziente['relazione_ai'])
        
    return pdf.output(dest='S').encode('latin-1')
