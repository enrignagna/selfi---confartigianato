from questionario_app.constants import (
    MAPPA_FORMAZIONE_40,
    MAPPA_GESTIONE_CLIENTI,
    MAPPA_PROCESSI_DECISIONALI,
    MAPPA_RD,
    MAPPA_RESPONSABILE_DIGITALE,
    MAPPA_SCALA_MATURITA,
    MAPPA_STRATEGIA_DIGITALE,
    MAPPA_TECNOLOGIE,
    MAPPA_USO_DATI_CLIENTI,
)


def media_valori(valori):
    validi = [v for v in valori if isinstance(v, (int, float))]
    if not validi:
        return None
    return round(sum(validi) / len(validi), 2)


def punteggio_scala_maturita(risposte, chiave):
    return MAPPA_SCALA_MATURITA.get(risposte.get(chiave))


def punteggio_mappa(risposte, chiave, mappa):
    return mappa.get(risposte.get(chiave))


def calcola_indice_tecnologie(risposte):
    tecnologie = risposte.get("tecnologie", {})
    if not tecnologie:
        return {"indice": None, "presenti": 0, "previste": 0, "totale": 0}

    punteggi = []
    presenti = 0
    previste = 0

    for stato in tecnologie.values():
        if stato in MAPPA_TECNOLOGIE:
            punteggi.append(MAPPA_TECNOLOGIE[stato])
        if stato == "Presente":
            presenti += 1
        elif stato == "Previsto entro 3 anni":
            previste += 1

    indice = round(sum(punteggi) / len(punteggi), 2) if punteggi else None
    return {
        "indice": indice,
        "presenti": presenti,
        "previste": previste,
        "totale": len(tecnologie),
    }


def calcola_dii(risposte):
    chiavi_dii = [
        "dii_addetti_connessi",
        "dii_ai",
        "dii_banda_larga",
        "dii_analisi_dati",
        "dii_cloud_base",
        "dii_cloud_intermedio_avanzato",
        "dii_social_media",
        "dii_erp",
        "dii_crm",
        "dii_due_social",
        "dii_vendite_online_1",
        "dii_vendite_b2c",
    ]

    totale_si = sum(1 for chiave in chiavi_dii if risposte.get(chiave) == "Si")
    if totale_si <= 3:
        livello = "Molto basso"
    elif totale_si <= 6:
        livello = "Basso"
    elif totale_si <= 9:
        livello = "Medio"
    else:
        livello = "Alto"

    return {"score": totale_si, "totale": len(chiavi_dii), "livello": livello}


def classifica_maturita(score):
    if score is None:
        return "Non calcolabile"
    if score < 2:
        return "Tradizionale"
    if score < 3:
        return "Digitalizzazione iniziale"
    if score < 4:
        return "Impresa digitalizzata"
    return "Impresa data-driven"


def calcola_indici_assessment(risposte):
    indice_amministrazione = media_valori(
        [
            punteggio_scala_maturita(risposte, "contabilita_finanza"),
            punteggio_mappa(risposte, "processi_decisionali", MAPPA_PROCESSI_DECISIONALI),
        ]
    )

    indice_mercato_clienti = media_valori(
        [
            punteggio_mappa(risposte, "gestione_clienti", MAPPA_GESTIONE_CLIENTI),
            punteggio_mappa(risposte, "uso_dati_clienti", MAPPA_USO_DATI_CLIENTI),
            punteggio_scala_maturita(risposte, "marketing"),
            punteggio_scala_maturita(risposte, "vendite"),
            punteggio_scala_maturita(risposte, "assistenza_post_vendita"),
        ]
    )

    dettaglio_tecnologie = calcola_indice_tecnologie(risposte)
    indice_tecnologie_innovazione = media_valori(
        [
            punteggio_scala_maturita(risposte, "sistemi_informativi"),
            punteggio_scala_maturita(risposte, "ricerca_sviluppo"),
            punteggio_mappa(risposte, "strategia_digitale", MAPPA_STRATEGIA_DIGITALE),
            dettaglio_tecnologie["indice"] * 5 if dettaglio_tecnologie["indice"] is not None else None,
            punteggio_mappa(risposte, "rd_governance", MAPPA_RD),
            punteggio_mappa(risposte, "rd_responsabile", MAPPA_RD),
            punteggio_mappa(risposte, "rd_metodo", MAPPA_RD),
            punteggio_mappa(risposte, "rd_digitale", MAPPA_RD),
        ]
    )

    indice_competenze = media_valori(
        [
            punteggio_scala_maturita(risposte, "gestione_personale"),
            punteggio_mappa(risposte, "responsabile_digitale", MAPPA_RESPONSABILE_DIGITALE),
            punteggio_mappa(risposte, "formazione_40", MAPPA_FORMAZIONE_40),
        ]
    )

    punteggi_operazioni = [
        punteggio_scala_maturita(risposte, "gestione_fornitori"),
        punteggio_scala_maturita(risposte, "gestione_acquisti"),
        punteggio_scala_maturita(risposte, "valutazione_fornitori"),
        punteggio_scala_maturita(risposte, "produzione_servizi"),
        punteggio_scala_maturita(risposte, "controllo_qualita"),
        punteggio_scala_maturita(risposte, "manutenzione"),
    ]

    if risposte.get("logistica_applicabile") == "Si":
        punteggi_operazioni.extend(
            [
                punteggio_scala_maturita(risposte, "logistica_interna"),
                punteggio_scala_maturita(risposte, "logistica_esterna"),
                punteggio_scala_maturita(risposte, "tracciabilita"),
            ]
        )

    indice_operazioni = media_valori(punteggi_operazioni)
    indici_area = {
        "Amministrazione": indice_amministrazione,
        "Mercato e clienti": indice_mercato_clienti,
        "Tecnologie e innovazione": indice_tecnologie_innovazione,
        "Competenze": indice_competenze,
        "Operazioni": indice_operazioni,
    }
    indice_complessivo = media_valori(list(indici_area.values()))

    return {
        "indice_complessivo": indice_complessivo,
        "livello_complessivo": classifica_maturita(indice_complessivo),
        "indici_area": indici_area,
        "dii": calcola_dii(risposte),
        "tecnologie": dettaglio_tecnologie,
    }
