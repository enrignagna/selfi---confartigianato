import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
import re

def nome_file_sicuro(testo):
    """
    Converte una stringa in un nome file sicuro:
    - minuscole
    - spazi -> _
    - rimuove caratteri non validi
    """
    testo = testo.lower().strip()
    testo = testo.replace(" ", "_")
    testo = re.sub(r"[^a-z0-9_]", "", testo)
    return testo






BLU_CONF = HexColor("#1170d0")
GRIGIO_TESTO = HexColor("#050F1B")

def genera_pdf_report(risposte):
    # Nome file con ragione sociale
    ragione_sociale = risposte.get("ragione_sociale", "impresa")
    nome_base = nome_file_sicuro(ragione_sociale)
    file_path = f"report_valutazione_{nome_base}.pdf"

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # --- STILI PERSONALIZZATI ---
    styles.add(ParagraphStyle(
        name="TitoloConf",
        fontSize=20,
        leading=24,
        textColor=BLU_CONF,
        spaceAfter=20,
        alignment=1  # center
    ))

    styles.add(ParagraphStyle(
        name="SottotitoloConf",
        fontSize=12,
        leading=14,
        textColor=GRIGIO_TESTO,
        spaceAfter=30,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        name="SezioneConf",
        fontSize=14,
        leading=18,
        textColor=BLU_CONF,
        spaceBefore=20,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name="TestoConf",
        fontSize=10,
        leading=14,
        textColor=GRIGIO_TESTO,
        spaceAfter=6
    ))

    story = []

    # ===============================
    # COPERTINA
    # ===============================
    try:
        logo = Image("confartigianato-logo.jpeg", width=6*cm, height=3*cm)
        logo.hAlign = "CENTER"
        story.append(logo)
        story.append(Spacer(1, 30))
    except:
        pass  # se il logo non viene trovato, il PDF viene comunque generato

    story.append(Paragraph(
        "Questionario di Valutazione Digitale",
        styles["TitoloConf"]
    ))

    story.append(Paragraph(
        "Digitalizzazione, innovazione e sostenibilità delle imprese",
        styles["SottotitoloConf"]
    ))

    if ragione_sociale:
        story.append(Paragraph(
            f"<b>Impresa:</b> {ragione_sociale}",
            styles["TestoConf"]
        ))

    story.append(PageBreak())

    # ===============================
    # CONTENUTO DEL REPORT
    # ===============================
    for chiave, valore in risposte.items():
        titolo = chiave.replace("_", " ").capitalize()

        story.append(Paragraph(titolo, styles["SezioneConf"]))

        if isinstance(valore, dict):
            for k, v in valore.items():
                story.append(Paragraph(f"<b>{k}</b>: {v}", styles["TestoConf"]))

        elif isinstance(valore, list):
            for v in valore:
                story.append(Paragraph(f"- {v}", styles["TestoConf"]))

        else:
            story.append(Paragraph(str(valore), styles["TestoConf"]))

    # ===============================
    # FOOTER ISTITUZIONALE
    # ===============================
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GRIGIO_TESTO)
        canvas.drawCentredString(
            A4[0] / 2,
            1.5 * cm,
            "© Confartigianato – Report di valutazione digitale"
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)

    return file_path
    


# ===============================
# CONFIGURAZIONE PAGINA
# ===============================   

st.set_page_config(
    page_title="Questionario di valutazione",
    layout="centered"
)

# ===============================
# HEADER CON LOGO CONFARTIGIANATO
# ===============================
col_logo, col_title = st.columns([1, 4])

with col_logo:
    st.image("confartigianato-logo.jpeg", width=120)

with col_title:
    st.title("Questionario di Valutazione Digitale")
    st.caption(
        "Sistema di assessment per la digitalizzazione, l’innovazione e la sostenibilità delle imprese"
    )

st.divider()

st.markdown(
    """
    <style>
    /* Titoli */
    h1, h2, h3 {
        color: f{BLU_CONF};
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f5f5f5;
    }

    /* Bottoni */
    button {
        border-radius: 6px;
        font-weight: 600;
    }

    /* Text area */
    textarea {
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ===============================
# STATO GLOBALE
# ===============================
if "risposte" not in st.session_state:
    st.session_state["risposte"] = {}

r = st.session_state["risposte"]

# ===============================
# NAVIGAZIONE
# ===============================
pagine = [
    "1. Anagrafica",
    "2. Contabilità e Finanza",
    "3. Clienti e Mercati",
    "4. Tecnologie",
    "5. Risorse Umane",
    "6. Acquisti",
    "7. Logistica",
    "8. Realizzazione prodotto / servizio",
    "9. Sostenibilità ambientale",
    "10. Conclusione",
    "Report finale"
]

pagina = st.sidebar.radio("Sezioni del questionario", pagine)

# ===============================
# SCALE STANDARD
# ===============================
scala_maturita = [
    "Attraverso consulenti/fornitori esterni o non sono realizzate",
    "Prevalentemente in modo non digitale",
    "In modo digitale senza integrazione con le altre funzioni aziendali",
    "In modo digitale con dati condivisi automaticamente con altre funzioni",
    "In modo digitale con integrazione completa e utilizzo automatico dei dati per decisioni e misurazione delle prestazioni"
]

# ===============================
# 1. ANAGRAFICA
# ===============================
if pagina == "1. Anagrafica":

    st.header("1. Anagrafica")

    r["ragione_sociale"] = st.text_input("Ragione sociale", r.get("ragione_sociale", ""))
    r["forma_societaria"] = st.radio(
        "Forma societaria",
        ["SRL", "SPA", "SRLs", "Sapa", "SNC", "SAS", "S.s.", "Società cooperativa", "Società consortile", "Altro"]
    )
    r["piva_cf"] = st.text_input("Codice fiscale / Partita IVA", r.get("piva_cf", ""))
    r["email_principale"] = st.text_input("Email principale", r.get("email_principale", ""))
    r["email_secondaria"] = st.text_input("Email secondaria", r.get("email_secondaria", ""))
    r["provincia"] = st.text_input("Provincia", r.get("provincia", ""))
    r["telefono"] = st.text_input("Telefono", r.get("telefono", ""))
    r["nome_compilatore"] = st.text_input("Nome compilatore", r.get("nome_compilatore", ""))
    r["cognome_compilatore"] = st.text_input("Cognome compilatore", r.get("cognome_compilatore", ""))
    r["ruolo_compilatore"] = st.text_input("Ruolo compilatore", r.get("ruolo_compilatore", ""))

    r["sedi"] = st.radio(
        "Sedi / stabilimenti",
        ["Unica sede", "Più sedi – valutazione globale", "Più sedi – valutazione per sede indicata"]
    )

    r["settore"] = st.radio(
        "Settore prevalente",
        [
            "A Agricoltura", "B Estrazione", "C Manifatturiero", "D Energia",
            "E Acqua e rifiuti", "F Costruzioni", "G Commercio", "H Trasporto",
            "I Alloggio e ristorazione", "J Informazione", "K Finanza",
            "L Immobiliare", "M Professionali", "N Supporto imprese",
            "O PA", "P Istruzione", "Q Sanità", "R Attività artistiche", "S Altri servizi"
        ]
    )

    r["addetti"] = st.radio("Numero addetti", ["0-9", "10-49", "50-249", "250-499", ">=500"])
    r["fatturato"] = st.radio(
        "Fatturato ultimo anno",
        ["<500k", "500k-1M", "1-2M", "2-5M", "5-10M", "10-25M", "25-50M", "50-100M", ">100M"]
    )
    r["mercato"] = st.radio("Tipo di mercato", ["B2C", "B2B"])

    # >>> AGGIUNTA NOTE
    r["note_anagrafica"] = st.text_area("Note aggiuntive – Anagrafica", r.get("note_anagrafica", ""))


# ===============================
# 2. CONTABILITÀ E FINANZA
# ===============================
elif pagina == "2. Contabilità e Finanza":

    st.header("2. Contabilità, Finanza e Processi decisionali")

    r["contabilita_finanza"] = st.radio("Gestione contabilità e finanza", scala_maturita)
    r["processi_decisionali"] = st.radio(
        "Processi decisionali",
        [
            "Basati sull’esperienza",
            "Basati su opportunità e concorrenti",
            "Strategia + dati di mercato",
            "Strategia + dati di mercato e interni",
            "Strategia proattiva e continua"
        ]
    )

    r["note_contabilita"] = st.text_area(
        "Note aggiuntive – Contabilità e Finanza",
        r.get("note_contabilita", "")
    )


# ===============================
# 3. CLIENTI E MERCATI
# ===============================
elif pagina == "3. Clienti e Mercati":

    st.header("3. Clienti e Mercati")

    r["marketing"] = st.radio("Marketing", scala_maturita)
    r["vendite"] = st.radio("Vendite", scala_maturita)
    r["assistenza_post_vendita"] = st.radio("Assistenza post vendita", scala_maturita)

    r["note_clienti_mercati"] = st.text_area(
        "Note aggiuntive – Clienti e Mercati",
        r.get("note_clienti_mercati", "")
    )


# ===============================
# 4. TECNOLOGIE + R&D
# ===============================
elif pagina == "4. Tecnologie":

    st.header("4. Tecnologie")

    r["sistemi_informativi"] = st.radio("Sistemi informativi", scala_maturita)
    r["ricerca_sviluppo"] = st.radio("Ricerca e sviluppo (livello generale)", scala_maturita)

    r["proprieta_intellettuale"] = st.multiselect(
        "Proprietà intellettuale",
        ["Brevetti", "Modelli", "Disegni", "Marchi", "Nessuna"]
    )

    # ---------- TECNOLOGIE ----------
    tecnologie = [
        "AI", "Blockchain", "Robotica", "Stampa 3D", "AR/VR", "Simulazione",
        "IoT", "Cloud", "Cybersicurezza", "Big Data", "CAD/CAM",
        "E-commerce", "Pagamenti digitali", "EDI", "Geolocalizzazione",
        "ERP", "WMS", "MES", "CRM/SCM/PLM", "RFID", "System integrator", "Altro"
    ]

    if "tecnologie" not in r:
        r["tecnologie"] = {}

    for t in tecnologie:
        r["tecnologie"][t] = st.selectbox(
            t,
            ["Non presente", "Presente", "Previsto entro 3 anni"],
            key=f"tech_{t}"
        )

    # ---------- R&D DETTAGLIATO ----------
    st.subheader("Ricerca, Sviluppo e Innovazione (R&D)")

    r["rd_governance"] = st.radio(
        "Livello di strutturazione delle attività di R&D",
        [
            "Nessuna attività di R&D",
            "Attività occasionali non strutturate",
            "Attività strutturate senza budget",
            "Attività strutturate con budget",
            "Funzione R&D formalizzata con KPI"
        ]
    )

    r["rd_responsabile"] = st.radio(
        "Responsabilità R&D",
        [
            "Nessuna",
            "Figura informale",
            "Figura formalmente nominata",
            "Team interno dedicato",
            "Team interno + collaborazioni esterne"
        ]
    )

    r["rd_metodo"] = st.radio(
        "Metodo di generazione e selezione delle idee",
        [
            "Nessun metodo",
            "Intuizioni informali",
            "Analisi di mercato",
            "Analisi dati interni/esterni",
            "Processi strutturati (design thinking, test pilota)"
        ]
    )

    r["rd_digitale"] = st.radio(
        "Supporto del digitale alle attività di R&D",
        [
            "Nessun supporto digitale",
            "Strumenti di base",
            "Software specialistici (CAD, simulazione, PLM)",
            "Integrazione con sistemi aziendali",
            "Uso avanzato di dati e AI"
        ]
    )

    r["rd_collaborazioni"] = st.multiselect(
        "Collaborazioni R&D",
        [
            "Nessuna",
            "Fornitori",
            "Clienti",
            "Università / centri di ricerca",
            "Startup / ecosistemi di innovazione"
        ]
    )

    # >>> AGGIUNTA: PROGETTI FUTURI R&D
    r["rd_progetti_futuri"] = st.text_area(
        "Progetti e idee future in ambito R&D",
        r.get("rd_progetti_futuri", "")
    )

    r["note_tecnologie"] = st.text_area(
        "Note aggiuntive – Tecnologie e R&D",
        r.get("note_tecnologie", "")
    )


# ===============================
# 5–10: NOTE FINALI PER OGNI SEZIONE
# ===============================
# (le altre sezioni restano IDENTICHE, con sola aggiunta delle note)

# 5. Risorse Umane
elif pagina == "5. Risorse Umane":
    st.header("5. Risorse Umane")
    r["gestione_personale"] = st.radio("Gestione del personale", scala_maturita)
    r["responsabile_digitale"] = st.radio("Responsabile trasformazione digitale", ["No", "No, ma sarà nominato", "Sì"])
    r["formazione_40"] = st.radio("Formazione Impresa 4.0", ["Già svolta", "Prevista entro 12 mesi", "Non valutata"])
    if r["formazione_40"] != "Non valutata":
        r["temi_formazione"] = st.multiselect("Temi formazione", ["Tecnologie hardware", "Tecnologie software", "Gestione dati", "Integrazione processi", "Altro"])
        r["figure_formate"] = st.multiselect("Figure coinvolte", ["Manager", "Responsabili di processo", "Operai", "Altro"])
    r["note_risorse_umane"] = st.text_area("Note aggiuntive – Risorse Umane", r.get("note_risorse_umane", ""))


# ===============================
# 6. ACQUISTI
# ===============================
elif pagina == "6. Acquisti":

    st.header("6. Acquisti")

    r["gestione_fornitori"] = st.radio("Gestione fornitori", scala_maturita)
    r["gestione_acquisti"] = st.radio("Gestione acquisti", scala_maturita)
    r["valutazione_fornitori"] = st.radio("Valutazione fornitori", scala_maturita)
    r["note_acquisti"] = st.text_area(
        "Note aggiuntive – Acquisti",
        r.get("note_acquisti", "")
    )
    

# ===============================
# 7. LOGISTICA
# ===============================
elif pagina == "7. Logistica":

    st.header("7. Logistica")

    r["logistica_applicabile"] = st.radio("La logistica si applica?", ["Sì", "No"])

    if r["logistica_applicabile"] == "Sì":
        r["logistica_interna"] = st.radio("Logistica interna", scala_maturita)
        r["logistica_esterna"] = st.radio("Logistica esterna", scala_maturita)
        r["tracciabilita"] = st.radio("Tracciabilità e magazzino", scala_maturita)
    r["note_logistica"] = st.text_area(
        "Note aggiuntive – Logistica",
        r.get("note_logistica", "")
    )   

# ===============================
# 8. PRODUZIONE / SERVIZIO
# ===============================
elif pagina == "8. Realizzazione prodotto / servizio":

    st.header("8. Realizzazione prodotto / servizio")

    r["produzione_servizi"] = st.radio("Produzione / erogazione", scala_maturita)
    r["controllo_qualita"] = st.radio("Controllo qualità", scala_maturita)
    r["manutenzione"] = st.radio("Manutenzione", scala_maturita)
    r["note_realizzazione"] = st.text_area(
        "Note aggiuntive – Realizzazione prodotto / servizio",
        r.get("note_realizzazione", "")
    )   

# ===============================
# 9. SOSTENIBILITÀ
# ===============================
elif pagina == "9. Sostenibilità ambientale":

    st.header("9. Sostenibilità ambientale")

    r["sostenibilita_digitale"] = st.radio(
        "Adozione tecnologie per sostenibilità",
        ["Sì", "No"]
    )

    if r["sostenibilita_digitale"] == "Sì":
        r["finalita_sostenibilita"] = st.multiselect(
            "Finalità",
            [
                "Sostenibilità processi",
                "Sostenibilità prodotti",
                "Conformità normativa"
            ]
        )

        r["risultati_sostenibilita"] = st.multiselect(
            "Risultati",
            [
                "Riduzione costi",
                "Aumento efficienza",
                "Miglioramento prodotti",
                "Aumento vendite",
                "Riqualificazione lavoratori",
                "Riduzione impatti ambientali",
                "Nessun risultato",
                "Altro"
            ]
        )
    if "Altro" in r["risultati_sostenibilita"]:
        r["risultati_sostenibilita_altro"] = st.text_input("Specificare altro")     
    r["note_sostenibilita"] = st.text_area(
        "Note aggiuntive – Sostenibilità ambientale",
        r.get("note_sostenibilita", "")
    )

# ===============================
# 10. CONCLUSIONE
# ===============================
elif pagina == "10. Conclusione":

    st.header("10. Conclusione")

    r["servizi_cciaa"] = st.multiselect(
        "Servizi CCIAA utilizzati",
        [
            "Eventi/corsi digitali",
            "Alternanza scuola-lavoro",
            "Internazionalizzazione",
            "Servizi digitali",
            "Altro"
        ]
    )

    if "Altro" in r["servizi_cciaa"]:
        r["servizi_cciaa_altro"] = st.text_input("Specificare altro")
    r["interesse_servizi"] = st.multiselect(
        "Servizi CCIAA di interesse",
        [   
            "Eventi/corsi digitali",
            "Alternanza scuola-lavoro",
            "Internazionalizzazione",
            "Servizi digitali",
            "Altro"
        ]
    )  
    if "Altro" in r["interesse_servizi"]:
        r["interesse_servizi_altro"] = st.text_input("Specificare altro")     
    r["note_conclusione"] = st.text_area(
        "Note aggiuntive – Conclusione",
        r.get("note_conclusione", "")
    )   

# ===============================
# REPORT FINALE
# ===============================
elif pagina == "Report finale":

    st.header("Report finale")

    # -------- REPORT TESTUALE --------
    report_txt = ""
    for k, v in r.items():
        report_txt += f"{k}: {v}\n"

    st.subheader("Report testuale")
    st.text_area("Anteprima", report_txt, height=300)

    st.download_button(
        "Scarica report testuale",
        data=report_txt,
        file_name="report_valutazione.txt",
        mime="text/plain"
    )

    # -------- REPORT PDF --------
    st.subheader("Report PDF")

    if st.button("Genera report PDF"):
        pdf_path = genera_pdf_report(r)

        with open(pdf_path, "rb") as f:
            st.download_button(
                "Scarica report PDF",
                data=f,
                file_name=pdf_path,
                mime="application/pdf"
            )