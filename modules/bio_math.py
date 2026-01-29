import math

def calcola_sella_idmatch(dit, dc_sx, dc_dx, idmatch_code):
    """Logica originale IDMATCH per selezione sella."""
    dc_media = (dc_sx + dc_dx) / 2
    
    if dc_media > 115: modello, shape = "SLR Boost", "T-Shape (Large Thighs)"
    elif dc_media >= 100: modello, shape = "Flite Boost", "V-Shape (Avg Thighs)"
    else: modello, shape = "Novus Boost", "Waved (Slim Thighs)"
    
    taglia_id = idmatch_code[0] # S o L
    numero = idmatch_code[1] # 1, 2, 3
    type_flow = "Fill" if numero == '1' else "Flow" if numero == '2' else "Superflow"
    
    width = "130-135mm" if taglia_id == 'S' else "145-150mm"
    
    return {
        "nome": f"{modello} {type_flow}",
        "specs": f"{shape} | ID: {idmatch_code}",
        "width_range": width
    }

def calcola_assetto_multidisciplina(disciplina, cav, tronco, braccio):
    """
    Calcola l'assetto variando i coefficienti in base alla disciplina.
    """
    # COEFFICIENTI BIOMECCANICI
    # Road: Standard Hinault/Lemond 0.885
    # MTB: Sella più bassa (0.880) per mobilità e pedali SPD. Reach più lungo telaio, stem corto.
    # Gravel: Via di mezzo (0.883). Comfort maggiore.
    # Chrono/TT: Sella alta (0.895) e avanzata per aprire l'angolo anca.
    
    coeffs = {
        "Road":   {"k_as": 0.885, "k_reach": 0.51, "k_drop": 0.10, "stem_std": 110, "setback_base": 6.5},
        "MTB":    {"k_as": 0.880, "k_reach": 0.46, "k_drop": 0.02, "stem_std": 60,  "setback_base": 5.0},
        "Gravel": {"k_as": 0.883, "k_reach": 0.49, "k_drop": 0.06, "stem_std": 90,  "setback_base": 6.0},
        "TT":     {"k_as": 0.895, "k_reach": 0.56, "k_drop": 0.18, "stem_std": 100, "setback_base": 2.5}
    }
    
    c = coeffs.get(disciplina, coeffs["Road"])
    
    # 1. ALTEZZA SELLA
    as_calc = round(cav * c['k_as'], 1)
    
    # 2. ARRETRAMENTO (Setback)
    # Stima base, poi va corretta col laser. Le TT sono molto avanzate.
    sk_calc = c['setback_base']
    
    # 3. DISTANZA SELLA-MANUBRIO (Reach Sella-Curva)
    # Formula base: (Tronco + Braccio) * coeff
    sy_calc = round((tronco + braccio) * c['k_reach'], 1)
    
    # 4. SCARTO (Drop)
    kw_calc = round(as_calc * c['k_drop'], 1)
    
    # 5. TELAIO IDEALE (Stima)
    ba_piantone = round(cav * 0.65, 1)
    if disciplina == "MTB": ba_piantone = round(cav * 0.58, 1) # Telai slooping
    
    bc_orizzontale = round(sy_calc - c['stem_std'] / 10 + 2, 1) # Stima orizzontale virtuale

    return {
        "AS": as_calc,
        "SK": sk_calc,
        "SY": sy_calc,
        "KW": kw_calc,
        "Stem": c['stem_std'],
        "Telaio_BA": ba_piantone,
        "Telaio_BC": bc_orizzontale
    }
