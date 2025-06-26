import spacy
from spacy.pipeline import EntityRuler
from pathlib import Path
from patterns.patterns_spacy import COMPOSED_PATTERNS, PRIMARY_PATTERNS
import os

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("pt_core_news_lg")

        # Only add custom ruler if it doesn't exist
        if "ruler_composed" not in _nlp.pipe_names:
            ruler_composed = _nlp.add_pipe("entity_ruler", name="ruler_composed", before="ner")
            from patterns.patterns_spacy import COMPOSED_PATTERNS
            ruler_composed.add_patterns(COMPOSED_PATTERNS)

        if "ruler_primary" not in _nlp.pipe_names:
            ruler_primary = _nlp.add_pipe("entity_ruler", name="ruler_primary", after="ruler_composed")
            from patterns.patterns_spacy import PRIMARY_PATTERNS
            ruler_primary.add_patterns(PRIMARY_PATTERNS)
    return _nlp


def extract_all_despachos(doc, filename, folder_path) -> list:
    results = []
    current_secretaria = None
    first_despacho = None
    second_occurrence_index = None

    des_ents = [ent for ent in doc.ents if ent.label_ == "DES"]
    secretaria_ents = [ent for ent in doc.ents if ent.label_ == "SECRETARIA"]
    all_ents = sorted(secretaria_ents + des_ents, key=lambda x: x.start)

    # Detecta primeira e segunda ocorrência
    for ent in all_ents:
        if ent.label_ == "DES":
            if first_despacho is None:
                first_despacho = ent.text.replace("\n", "").strip()
            elif ent.text.replace("\n", "").strip() == first_despacho:
                second_occurrence_index = ent.start
                break

    # Limita as entidades ao ponto de corte
    filtered_ents = [ent for ent in all_ents if second_occurrence_index is None or ent.start < second_occurrence_index]

    for i, ent in enumerate(filtered_ents):
        if ent.label_ == "SECRETARIA":
            current_secretaria = ent.text.replace("\n", " ").strip()

        elif ent.label_ == "DES" and current_secretaria:
            despacho_text = ent.text.replace("\n", "").strip()

            start = ent.start
            end = filtered_ents[i + 1].start if i + 1 < len(filtered_ents) else len(doc)
            chunk = doc[start:end].text.replace(current_secretaria, "").strip()

            record = {
                "despacho": despacho_text,
                "summary": "",
                "secretaria": current_secretaria,
                "PDF": filename,
                "path": os.path.join(folder_path, filename),
                "TEXT": "",
                "ANEXO": ""
            }
            results.append(record)

    return results


