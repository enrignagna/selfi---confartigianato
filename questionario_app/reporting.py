import json
import math
import os
import re
from datetime import datetime

import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer

from questionario_app.assessment import calcola_indici_assessment
from questionario_app.constants import BLU_CONF, GRIGIO_TESTO, ETICHETTE_RISPOSTE, ORDINE_CHIAVI_REPORT

OUTPUT_DIR = "generated_reports"


def nome_file_sicuro(testo):
    testo = testo.lower().strip()
    testo = testo.replace(" ", "_")
    return re.sub(r"[^a-z0-9_]", "", testo)


def etichetta_risposta(chiave):
    return ETICHETTE_RISPOSTE.get(chiave, chiave.replace("_", " ").capitalize())


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR


def _ordered_answers(risposte):
    ordered = {}

    for chiave in ORDINE_CHIAVI_REPORT:
        if chiave in risposte:
            ordered[chiave] = risposte[chiave]

    for chiave, valore in risposte.items():
        if chiave not in ordered:
            ordered[chiave] = valore

    return ordered


def build_report_payload(risposte):
    ragione_sociale = risposte.get("ragione_sociale", "impresa")
    nome_base = nome_file_sicuro(ragione_sociale)
    risposte_ordinate = _ordered_answers(risposte)

    return {
        "metadata": {
            "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "ragione_sociale": ragione_sociale,
            "output_basename": nome_base,
        },
        "risultati": calcola_indici_assessment(risposte),
        "risposte": risposte_ordinate,
        "risposte_etichettate": {etichetta_risposta(chiave): valore for chiave, valore in risposte_ordinate.items()},
    }


def genera_radar_chart(indici_area, file_path="radar_chart.png"):
    etichette = list(indici_area.keys())
    valori = [indici_area[k] if indici_area[k] is not None else 0 for k in etichette]
    if not valori:
        return None

    num_vars = len(etichette)
    angoli = [n / float(num_vars) * 2 * math.pi for n in range(num_vars)]
    angoli += angoli[:1]
    valori += valori[:1]

    plt.figure(figsize=(7, 7))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angoli[:-1], etichette)
    ax.set_rlabel_position(0)
    plt.yticks([1, 2, 3, 4, 5], ["1", "2", "3", "4", "5"])
    plt.ylim(0, 5)
    ax.plot(angoli, valori, linewidth=2)
    ax.fill(angoli, valori, alpha=0.25)
    plt.title("Radar di maturita digitale", pad=20)
    plt.tight_layout()
    plt.savefig(file_path, dpi=150, bbox_inches="tight")
    plt.close()
    return file_path


def build_pdf_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitoloConf",
            fontSize=20,
            leading=24,
            textColor=BLU_CONF,
            spaceAfter=20,
            alignment=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SottotitoloConf",
            fontSize=12,
            leading=14,
            textColor=GRIGIO_TESTO,
            spaceAfter=30,
            alignment=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SezioneConf",
            fontSize=14,
            leading=18,
            textColor=BLU_CONF,
            spaceBefore=18,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TestoConf",
            fontSize=10,
            leading=14,
            textColor=GRIGIO_TESTO,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="VoceConf",
            fontSize=10,
            leading=14,
            textColor=GRIGIO_TESTO,
            leftIndent=10,
            spaceAfter=4,
        )
    )
    return styles


def _build_story_header(story, styles, ragione_sociale):
    try:
        logo = Image("images/dih-logo.jpg", width=6 * cm, height=3 * cm)
        logo.hAlign = "CENTER"
        story.append(logo)
        story.append(Spacer(1, 30))
    except Exception:
        pass

    story.append(Paragraph("Questionario di Valutazione Digitale", styles["TitoloConf"]))
    story.append(
        Paragraph(
            "Digitalizzazione, innovazione e sostenibilita delle imprese",
            styles["SottotitoloConf"],
        )
    )

    if ragione_sociale:
        story.append(Paragraph(f"<b>Impresa:</b> {ragione_sociale}", styles["TestoConf"]))

    story.append(PageBreak())


def _build_story_results(story, styles, risultati, radar_path):
    story.append(Paragraph("Risultati dell'assessment digitale", styles["SezioneConf"]))
    story.append(
        Paragraph(
            f"<b>Indice di maturita digitale complessiva:</b> {risultati['indice_complessivo']} / 5",
            styles["TestoConf"],
        )
    )
    story.append(Paragraph(f"<b>Livello complessivo:</b> {risultati['livello_complessivo']}", styles["TestoConf"]))
    story.append(Paragraph("Indici per area", styles["SezioneConf"]))

    for area, valore in risultati["indici_area"].items():
        story.append(Paragraph(f"<b>{area}</b>: {valore} / 5", styles["TestoConf"]))

    story.append(Paragraph("Digital Intensity Index (DII)", styles["SezioneConf"]))
    story.append(
        Paragraph(
            f"<b>Indicatori soddisfatti:</b> {risultati['dii']['score']} / {risultati['dii']['totale']}",
            styles["TestoConf"],
        )
    )
    story.append(Paragraph(f"<b>Livello DII:</b> {risultati['dii']['livello']}", styles["TestoConf"]))

    story.append(Paragraph("Diffusione tecnologica", styles["SezioneConf"]))
    story.append(Paragraph(f"<b>Indice di diffusione tecnologica:</b> {risultati['tecnologie']['indice']}", styles["TestoConf"]))
    story.append(
        Paragraph(
            f"<b>Tecnologie presenti:</b> {risultati['tecnologie']['presenti']} / {risultati['tecnologie']['totale']}",
            styles["TestoConf"],
        )
    )
    story.append(
        Paragraph(
            f"<b>Tecnologie previste entro 3 anni:</b> {risultati['tecnologie']['previste']}",
            styles["TestoConf"],
        )
    )

    if radar_path and os.path.exists(radar_path):
        story.append(Paragraph("Radar di maturita digitale", styles["SezioneConf"]))
        img = Image(radar_path, width=13 * cm, height=13 * cm)
        img.hAlign = "CENTER"
        story.append(img)

    story.append(PageBreak())


def _build_story_answers(story, styles, risposte):
    story.append(Paragraph("Risposte complete al questionario", styles["SezioneConf"]))

    for chiave in ORDINE_CHIAVI_REPORT:
        if chiave not in risposte:
            continue

        valore = risposte.get(chiave)
        story.append(Paragraph(etichetta_risposta(chiave), styles["SezioneConf"]))

        if isinstance(valore, dict):
            if not valore:
                story.append(Paragraph("Nessuna risposta", styles["TestoConf"]))
            else:
                for k, v in valore.items():
                    story.append(Paragraph(f"<b>{k}</b>: {v}", styles["VoceConf"]))
        elif isinstance(valore, list):
            if not valore:
                story.append(Paragraph("Nessuna risposta", styles["TestoConf"]))
            else:
                for voce in valore:
                    story.append(Paragraph(f"- {voce}", styles["VoceConf"]))
        else:
            testo = str(valore).strip() if valore is not None else ""
            story.append(Paragraph(testo if testo else "Nessuna risposta", styles["TestoConf"]))


def genera_pdf_report(risposte):
    payload = build_report_payload(risposte)
    ragione_sociale = payload["metadata"]["ragione_sociale"]
    nome_base = payload["metadata"]["output_basename"]
    output_dir = ensure_output_dir()
    file_path = os.path.join(output_dir, f"report_valutazione_{nome_base}.pdf")
    radar_path = os.path.join(output_dir, f"radar_{nome_base}.png")

    risultati = payload["risultati"]
    radar_generato = genera_radar_chart(risultati["indici_area"], radar_path)
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = build_pdf_styles()
    story = []
    _build_story_header(story, styles, ragione_sociale)
    _build_story_results(story, styles, risultati, radar_generato)
    _build_story_answers(story, styles, risposte)

    def footer(canvas, _doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GRIGIO_TESTO)
        canvas.drawCentredString(
            A4[0] / 2,
            1.5 * cm,
            "© Digital Innovation Hub - Confartigianato - Report di valutazione digitale",
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return file_path


def genera_json_report(risposte):
    payload = build_report_payload(risposte)
    nome_base = payload["metadata"]["output_basename"]
    output_dir = ensure_output_dir()
    file_path = os.path.join(output_dir, f"report_valutazione_{nome_base}.json")

    with open(file_path, "w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, ensure_ascii=False, indent=2)

    return file_path
