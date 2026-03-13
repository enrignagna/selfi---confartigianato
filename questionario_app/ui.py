import os

import streamlit as st

from questionario_app.assessment import calcola_indici_assessment
from questionario_app.constants import BLU_CONF_HEX, PAGINE, SCALA_MATURITA, TECNOLOGIE_OPZIONI
from questionario_app.reporting import ensure_output_dir, genera_json_report, genera_pdf_report, genera_radar_chart


def configure_page():
    st.set_page_config(page_title="Questionario di valutazione", layout="centered")


def render_header():
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image("images/dih-logo.jpg", width=120)
    with col_title:
        st.title("Questionario di Valutazione Digitale")
        st.caption(
            "Sistema di assessment per la digitalizzazione, l'innovazione e la sostenibilita delle imprese"
        )

    st.divider()
    st.markdown(
        f"""
        <style>
        h1, h2, h3 {{
            color: {BLU_CONF_HEX};
        }}

        section[data-testid="stSidebar"] {{
            background-color: #f5f5f5;
        }}

        button {{
            border-radius: 6px;
            font-weight: 600;
        }}

        textarea {{
            border-radius: 6px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_risposte():
    if "risposte" not in st.session_state:
        st.session_state["risposte"] = {}
    return st.session_state["risposte"]


def render_sidebar():
    return st.sidebar.radio("Sezioni del questionario", PAGINE)


def text_input_field(risposte, key, label):
    risposte[key] = st.text_input(label, value=risposte.get(key, ""))


def text_area_field(risposte, key, label):
    risposte[key] = st.text_area(label, value=risposte.get(key, ""))


def radio_field(risposte, key, label, options):
    current = risposte.get(key)
    index = options.index(current) if current in options else 0
    risposte[key] = st.radio(label, options, index=index)


def multiselect_field(risposte, key, label, options):
    default = risposte.get(key, [])
    risposte[key] = st.multiselect(label, options, default=default)


def render_anagrafica(risposte):
    st.header("1. Anagrafica")
    text_input_field(risposte, "ragione_sociale", "Ragione sociale")
    radio_field(
        risposte,
        "forma_societaria",
        "Forma societaria",
        [
            "SRL",
            "SPA",
            "SRLs",
            "Sapa",
            "SNC",
            "SAS",
            "S.s.",
            "Societa cooperativa",
            "Societa consortile",
            "Ditta individuale",
            "Libero professionista",
            "Associazione",
            "Fondazione",
            "Altro",
        ],
    )
    text_input_field(risposte, "piva_cf", "Codice fiscale / Partita IVA")
    text_input_field(risposte, "email_principale", "Email principale")
    text_input_field(risposte, "comune", "Comune")
    text_input_field(risposte, "provincia", "Provincia")
    text_input_field(risposte, "regione", "Regione")
    text_input_field(risposte, "telefono", "Telefono")
    text_input_field(risposte, "nome_compilatore", "Nome compilatore")
    text_input_field(risposte, "cognome_compilatore", "Cognome compilatore")
    text_input_field(risposte, "ruolo_compilatore", "Ruolo compilatore")
    radio_field(
        risposte,
        "sedi",
        "Sedi / stabilimenti",
        ["Unica sede", "Piu sedi - valutazione globale", "Piu sedi - valutazione per sede indicata"],
    )
    text_input_field(risposte, "codice_ateco", "Codice ATECO")
    radio_field(
        risposte,
        "settore",
        "Settore prevalente",
        [
            "Agricoltura",
            "Estrazione",
            "Manifatturiero",
            "Energia",
            "Acqua e rifiuti",
            "Costruzioni",
            "Commercio",
            "Trasporto",
            "Alloggio e ristorazione",
            "Informazione",
            "Finanza",
            "Immobiliare",
            "Professionali",
            "Supporto imprese",
            "PA",
            "Istruzione",
            "Sanita",
            "Attivita artistiche",
            "Servizi",
            "ICT",
            "Benessere",
            "Impianti",
            "Altri servizi",
        ],
    )
    radio_field(risposte, "addetti", "Numero addetti", ["0-9", "10-49", "50-249", ">=250"])
    radio_field(
        risposte,
        "fatturato",
        "Fatturato ultimo anno",
        ["<500k", "500k-1M", "1-2M", "2-5M", "5-10M", "10-25M", "25-50M", "50-100M", ">100M"],
    )
    radio_field(risposte, "mercato", "Tipo di mercato", ["B2C", "B2B", "Entrambi"])
    text_area_field(risposte, "note_anagrafica", "Note aggiuntive - Anagrafica")


def render_contabilita(risposte):
    st.header("2. Servizi Tradizionali")
    radio_field(risposte, "servizi_tradizionali", "Gestione servizi tradizionali", SCALA_MATURITA)
    multiselect_field(
        risposte,
        "strumenti_amministrativi",
        "Quali strumenti digitali vengono utilizzati per la gestione amministrativa?",
        [
            "Fogli Excel",
            "Software gestionale contabile",
            "ERP aziendale",
            "Portale fatturazione elettronica",
            "Gestione documentale digitale",
            "Integrazione con banca / pagamenti digitali",
            "Nessuno strumento digitale specifico",
        ],
    )
    radio_field(
        risposte,
        "processi_decisionali",
        "Su cosa si basano principalmente le decisioni aziendali?",
        [
            "Esperienza e intuizione",
            "Osservazione di opportunita e concorrenti",
            "Strategia supportata da dati di mercato",
            "Strategia supportata da dati di mercato e dati interni",
            "Strategia proattiva basata su analisi continua dei dati",
        ],
    )
    radio_field(
        risposte,
        "gestione_attivita",
        "Come viene gestita l'attività aziendale?",
        ["Internamente", "Internamente con supporto esterno", "Studio esterno"],
    )
    multiselect_field(
        risposte,
        "confartigianato_servizio",
        "Quali servizi sono gestiti da Confartigianato?",
        ["Sicurezza", "Energia", "Contabilita", "Paghe", "Consulenza finanziaria", "Supporto gestionale", "Credito", "Nessuno"],
    )
    text_area_field(risposte, "note_contabilita", "Note aggiuntive - Contabilita e Finanza")


def render_clienti_mercati(risposte):
    st.header("3. Clienti e Mercati")
    multiselect_field(
        risposte,
        "strumenti_clienti",
        "Quali strumenti utilizzate per gestire i clienti?",
        [
            "Rubrica",
            "Email",
            "Fogli Excel",
            "Software gestionale aziendale",
            "CRM",
            "Piattaforme di email marketing",
            "Strumenti di assistenza clienti (ticketing)",
            "Nessuno strumento specifico",
        ],
    )
    multiselect_field(
        risposte,
        "presenza_digitale",
        "Quali canali digitali utilizza l'azienda per comunicare con il mercato?",
        [
            "Sito web aziendale",
            "E-commerce",
            "Social media",
            "Newsletter",
            "Marketplace online",
            "Nessun canale digitale",
        ],
    )
    radio_field(
        risposte,
        "uso_dati_clienti",
        "Come vengono utilizzati i dati dei clienti?",
        [
            "Non vengono raccolti o analizzati",
            "Raccolti ma usati raramente",
            "Utilizzati per alcune decisioni commerciali",
            "Analizzati regolarmente",
            "Utilizzati in modo sistematico per strategie commerciali",
        ],
    )
    radio_field(
        risposte,
        "analisi_mercato",
        "Come l'azienda monitora il mercato e i concorrenti?",
        [
            "Non viene effettuato monitoraggio",
            "Monitoraggio informale",
            "Analisi occasionali",
            "Analisi periodiche",
            "Monitoraggio continuo con strumenti digitali",
        ],
    )
    radio_field(risposte, "marketing", "Marketing", SCALA_MATURITA)
    radio_field(risposte, "vendite", "Vendite", SCALA_MATURITA)
    radio_field(risposte, "assistenza_post_vendita", "Assistenza post vendita", SCALA_MATURITA)
    text_area_field(risposte, "note_clienti_mercati", "Note aggiuntive - Clienti e Mercati")


def render_tecnologie(risposte):
    st.header("4. Tecnologie e Innovazione")
    radio_field(
        risposte,
        "sistemi_informativi",
        "Livello di digitalizzazione e integrazione dei sistemi informativi aziendali",
        SCALA_MATURITA,
    )
    radio_field(
        risposte,
        "ricerca_sviluppo",
        "Livello generale delle attivita di ricerca, sviluppo e innovazione",
        SCALA_MATURITA,
    )
    radio_field(
        risposte,
        "strategia_digitale",
        "L'impresa ha una strategia digitale o di innovazione formalizzata?",
        ["No", "In fase di definizione", "Si, ma non formalizzata", "Si, formalizzata", "Si, formalizzata e monitorata con KPI"],
    )
    multiselect_field(
        risposte,
        "proprieta_intellettuale",
        "Proprieta intellettuale posseduta dall'impresa",
        ["Brevetti", "Modelli di utilita", "Disegni industriali", "Marchi registrati", "Nessuna"],
    )

    st.subheader("Tecnologie adottate o previste")
    if "tecnologie" not in risposte:
        risposte["tecnologie"] = {}
    for tecnologia in TECNOLOGIE_OPZIONI:
        corrente = risposte["tecnologie"].get(tecnologia, "Non presente")
        index = ["Non presente", "Presente", "Previsto entro 3 anni"].index(corrente)
        risposte["tecnologie"][tecnologia] = st.selectbox(
            tecnologia,
            ["Non presente", "Presente", "Previsto entro 3 anni"],
            index=index,
            key=f"tech_{tecnologia}",
        )

    st.subheader("Ricerca, Sviluppo e Innovazione (R&D)")
    radio_field(risposte, "rd_applicabile", "La Ricerca e Sviluppo si applica?", ["Si", "No"])
    if risposte["rd_applicabile"] == "Si":
        radio_field(
            risposte,
            "rd_governance",
            "Livello di strutturazione delle attivita di R&D",
            [
                "Nessuna attivita di R&D",
                "Attivita occasionali non strutturate",
                "Attivita strutturate senza budget",
                "Attivita strutturate con budget",
                "Funzione R&D formalizzata con KPI",
            ],
        )
        radio_field(
            risposte,
            "rd_responsabile",
            "Responsabilita R&D",
            ["Nessuna", "Figura informale", "Figura formalmente nominata", "Team interno dedicato", "Team interno + collaborazioni esterne"],
        )
        radio_field(
            risposte,
            "rd_metodo",
            "Metodo di generazione e selezione delle idee",
            ["Nessun metodo", "Intuizioni informali", "Analisi di mercato", "Analisi dati interni/esterni", "Processi strutturati (design thinking, test pilota)"],
        )
        radio_field(
            risposte,
            "rd_digitale",
            "Utilizzo di strumenti digitali nelle attivita di ricerca e sviluppo",
            ["Nessun supporto digitale", "Strumenti di base", "Software specialistici (CAD, simulazione, PLM)", "Integrazione con sistemi aziendali", "Uso avanzato di dati e AI"],
        )
        multiselect_field(
        risposte,
        "rd_collaborazioni",
        "Collaborazioni R&D",
        ["Nessuna", "Fornitori", "Clienti", "Universita / centri di ricerca", "Startup / ecosistemi di innovazione"],
        )
        text_area_field(risposte, "rd_progetti_futuri", "Progetti e idee future in ambito R&D")
    text_area_field(risposte, "note_tecnologie", "Note aggiuntive - Tecnologie e R&D")


def render_risorse_umane(risposte):
    st.header("5. Risorse Umane")
    radio_field(risposte, "hr_applicabile", "Le risorse umane si applicano?", ["Si", "No"])
    if risposte["hr_applicabile"] == "Si":
        radio_field(risposte, "gestione_personale", "Digitalizzazione dei processi di gestione del personale", SCALA_MATURITA)
        radio_field(risposte, "responsabile_digitale", "Responsabile trasformazione digitale", ["No", "No, ma sara nominato", "Si"])
        radio_field(risposte, "formazione_40", "Formazione Impresa 4.0", ["Gia svolta", "Prevista entro 12 mesi", "Non valutata"])
        if risposte["formazione_40"] != "Non valutata":
            multiselect_field(
                risposte,
                "temi_formazione",
                "Temi formazione",
                ["Tecnologie hardware", "Tecnologie software", "Gestione dati", "Integrazione processi", "Altro"],
            )
            multiselect_field(
                risposte,
                "figure_formate",
                "Figure coinvolte",
                ["Manager", "Responsabili di processo", "Operai", "Altro"],
            )
        text_area_field(risposte, "note_risorse_umane", "Note aggiuntive - Risorse Umane")


def render_acquisti(risposte):
    st.header("6. Acquisti")
    radio_field(risposte, "acquisti_applicabile", "Gli acquisti si applicano?", ["Si", "No"])
    if risposte["acquisti_applicabile"] == "Si":
        radio_field(risposte, "gestione_fornitori", "Gestione fornitori", SCALA_MATURITA)
        radio_field(risposte, "gestione_acquisti", "Gestione acquisti", SCALA_MATURITA)
        radio_field(risposte, "valutazione_fornitori", "Valutazione fornitori", SCALA_MATURITA)
        text_area_field(risposte, "note_acquisti", "Note aggiuntive - Acquisti")


def render_logistica(risposte):
    st.header("7. Logistica")
    radio_field(risposte, "logistica_applicabile", "La logistica si applica?", ["Si", "No"])
    if risposte["logistica_applicabile"] == "Si":
        radio_field(risposte, "logistica_interna", "Logistica interna", SCALA_MATURITA)
        radio_field(risposte, "logistica_esterna", "Logistica esterna", SCALA_MATURITA)
        radio_field(risposte, "tracciabilita", "Tracciabilita dei materiali e gestione del magazzino", SCALA_MATURITA)
        text_area_field(risposte, "note_logistica", "Note aggiuntive - Logistica")


def render_realizzazione(risposte):
    st.header("8. Realizzazione prodotto / servizio")
    radio_field(risposte, "prodotto_digitale", "Sviluppo di prodotto e/o servizio", ["Si", "No"])
    if risposte["prodotto_digitale"] == "Si":
        radio_field(risposte, "produzione_servizi", "Produzione o erogazione del servizio", SCALA_MATURITA)
        radio_field(risposte, "controllo_qualita", "Controllo qualita", SCALA_MATURITA)
        radio_field(risposte, "manutenzione", "Manutenzione", SCALA_MATURITA)
        text_area_field(risposte, "note_realizzazione", "Note aggiuntive - Realizzazione prodotto / servizio")


def render_sostenibilita(risposte):
    st.header("9. Sostenibilita ambientale")
    radio_field(risposte, "sostenibilita_digitale", "Adozione tecnologie per sostenibilita", ["Si", "No"])
    if risposte["sostenibilita_digitale"] == "Si":
        multiselect_field(
            risposte,
            "finalita_sostenibilita",
            "Finalita",
            ["Sostenibilita processi", "Sostenibilita prodotti", "Conformita normativa"],
        )
        multiselect_field(
            risposte,
            "risultati_sostenibilita",
            "Risultati",
            [
                "Riduzione costi",
                "Aumento efficienza",
                "Miglioramento prodotti",
                "Aumento vendite",
                "Riqualificazione lavoratori",
                "Riduzione impatti ambientali",
                "Nessun risultato",
                "Altro",
            ],
        )
    if "Altro" in risposte.get("risultati_sostenibilita", []):
        text_input_field(risposte, "risultati_sostenibilita_altro", "Specificare altro")
    text_area_field(risposte, "note_sostenibilita", "Note aggiuntive - Sostenibilita ambientale")


def render_dii(risposte):
    st.header("Digital Intensity Index")
    st.markdown(
        "Le seguenti domande fanno riferimento agli indicatori ufficiali del Digital Intensity Index (DII) utilizzati a livello europeo."
    )
    radio_field(risposte, "dii_addetti_connessi", "1. Gli addetti che lavorano connessi alla rete sono piu del 50%?", ["Si", "No"])
    radio_field(risposte, "dii_ai", "2. L'impresa utilizza tecnologie di Intelligenza Artificiale (qualsiasi)?", ["Si", "No"])
    radio_field(risposte, "dii_banda_larga", "3. Connessione Internet fissa con velocita di download >= 30 Mbit/s?", ["Si", "No"])
    radio_field(risposte, "dii_analisi_dati", "4. L'impresa realizza analisi dei dati per modelli, previsioni e supporto decisionale?", ["Si", "No"])

    st.subheader("Cloud computing")
    st.markdown(
        """
        **Cloud di base**: posta elettronica, PEC, software per ufficio, archiviazione file
        **Cloud intermedio**: software di finanza/contabilita, ERP, CRM
        **Cloud sofisticato**: hosting database, piattaforme per sviluppo e test applicazioni
        """
    )
    radio_field(risposte, "dii_cloud_base", "5. L'impresa acquista servizi di cloud computing?", ["Si", "No"])
    radio_field(risposte, "dii_cloud_intermedio_avanzato", "6. L'impresa acquista servizi di cloud computing intermedi o sofisticati?", ["Si", "No"])

    st.subheader("Social media e sistemi gestionali")
    radio_field(risposte, "dii_social_media", "7. L'impresa utilizza almeno un social media?", ["Si", "No"])
    radio_field(risposte, "dii_erp", "8. L'impresa utilizza un ERP per condividere informazioni tra aree funzionali?", ["Si", "No"])
    radio_field(risposte, "dii_crm", "9. L'impresa dispone di un CRM?", ["Si", "No"])
    radio_field(risposte, "dii_due_social", "10. L'impresa utilizza almeno due social media?", ["Si", "No"])

    st.subheader("Vendite online")
    radio_field(risposte, "dii_vendite_online_1", "11. Le vendite online sono >= 1% dei ricavi totali?", ["Si", "No"])
    radio_field(risposte, "dii_vendite_b2c", "12. Le vendite via web sono > 1% dei ricavi e il B2C e > 10% delle vendite online?", ["Si", "No"])


def render_report_finale(risposte):
    st.header("Report finale")
    risultati = calcola_indici_assessment(risposte)
    output_dir = ensure_output_dir()

    st.subheader("Risultati dell'assessment digitale")
    st.write(f"**Indice di maturita digitale complessiva:** {risultati['indice_complessivo']} / 5")
    st.write(f"**Livello complessivo:** {risultati['livello_complessivo']}")

    st.subheader("Indici per area")
    for area, valore in risultati["indici_area"].items():
        st.write(f"**{area}:** {valore} / 5")

    st.subheader("Digital Intensity Index (DII)")
    st.write(f"**Indicatori soddisfatti:** {risultati['dii']['score']} / {risultati['dii']['totale']}")
    st.write(f"**Livello DII:** {risultati['dii']['livello']}")

    st.subheader("Diffusione tecnologica")
    st.write(f"**Indice di diffusione tecnologica:** {risultati['tecnologie']['indice']}")
    st.write(f"**Tecnologie presenti:** {risultati['tecnologie']['presenti']} / {risultati['tecnologie']['totale']}")
    st.write(f"**Tecnologie previste entro 3 anni:** {risultati['tecnologie']['previste']}")

    radar_preview = genera_radar_chart(
        risultati["indici_area"],
        os.path.join(output_dir, "radar_preview.png"),
    )
    if radar_preview and os.path.exists(radar_preview):
        st.subheader("Radar di maturita digitale")
        st.image(radar_preview, width=600)

    st.subheader("Report esportabili")
    st.caption(f"I file generati vengono salvati in: `{output_dir}`")
    if st.button("Genera report PDF"):
        pdf_path = genera_pdf_report(risposte)
        with open(pdf_path, "rb") as file_handle:
            st.download_button(
                "Scarica report PDF",
                data=file_handle.read(),
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
            )

    if st.button("Genera report JSON"):
        json_path = genera_json_report(risposte)
        with open(json_path, "rb") as file_handle:
            st.download_button(
                "Scarica report JSON",
                data=file_handle.read(),
                file_name=os.path.basename(json_path),
                mime="application/json",
            )


def render_page(pagina, risposte):
    renderers = {
        "1. Anagrafica": render_anagrafica,
        "2. Contabilita e Finanza": render_contabilita,
        "3. Clienti e Mercati": render_clienti_mercati,
        "4. Tecnologie": render_tecnologie,
        "5. Risorse Umane": render_risorse_umane,
        "6. Acquisti": render_acquisti,
        "7. Logistica": render_logistica,
        "8. Realizzazione prodotto / servizio": render_realizzazione,
        "9. Sostenibilita ambientale": render_sostenibilita,
        "Digital Intensity Index": render_dii,
        "Report finale": render_report_finale,
    }
    renderers[pagina](risposte)
