import spacy
from spacy.pipeline import EntityRuler
from pathlib import Path
from patterns.patterns_spacy import COMPOSED_PATTERNS, PRIMARY_PATTERNS
_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("pt_core_news_lg")
        ruler1 = _nlp.add_pipe("entity_ruler", before="ner")
        ruler1.add_patterns(COMPOSED_PATTERNS)
        ruler2 = _nlp.add_pipe("entity_ruler", after="ruler1")
        ruler2.add_patterns(PRIMARY_PATTERNS)
    return _nlp

def extract_all_despachos(doc, filename, folder_path) -> list:
    results = []
    current_secretaria = None
    des_ents = [ent for ent in doc.ents if ent.label_ == "DES"]
    secretaria_ents = [ent for ent in doc.ents if ent.label_ == "SECRETARIA"]
    all_ents = sorted(secretaria_ents + des_ents, key=lambda x: x.start)

    for i, ent in enumerate(all_ents):
        if ent.label_ == "SECRETARIA":
            current_secretaria = ent.text
        elif ent.label_ == "DES" and current_secretaria:
            start = ent.start
            end = all_ents[i + 1].start if i + 1 < len(all_ents) else len(doc)
            chunk = doc[start:end].text.replace(current_secretaria, "").strip()
            record = {
                "despacho": ent.text.replace("\n", "").strip(),
                "summary": "",
                "secretaria": current_secretaria,
                "PDF": filename,
                "path": os.path.join(folder_path, filename),
                "TEXT": "",
                "ANEXO": ""
            }
            results.append(record)
    return results
