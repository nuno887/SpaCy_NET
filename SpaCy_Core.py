import os
import pdfplumber

import spacy
from spacy.pipeline import EntityRuler
import json

from PATTERNS_SpaCy import COMPOSED_PATTERNS, PRIMARY_PATTERNS


nlp = spacy.load("pt_core_news_lg")


# Add composed/override patterns first
ruler_composed = nlp.add_pipe("entity_ruler", name="ruler_composed", before="ner")
ruler_composed.add_patterns(COMPOSED_PATTERNS)

# Add general/primary patterns second
ruler_primary = nlp.add_pipe("entity_ruler", name="ruler_primary", after="ruler_composed")
ruler_primary.add_patterns(PRIMARY_PATTERNS)


#====================================================== pdfPlumber ===================================================================================

def extract_text_from_pdf(input_dir: str, output_dir: str) -> None:
    """
    Extracts raw text from all PDF files in the input_dir and saves them
    as .txt files in the output_dir — skipping files that already exist.
    
    Parameters:
        input_dir (str): Directory containing PDF files.
        output_dir (str): Directory to save extracted raw text files.
    """
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    files = os.listdir(input_dir)
    if not files:
        print(f"⚠️ No PDF files found in '{input_dir}'")
        return

    for filename in files:
        if not filename.lower().endswith(".pdf"):
            print(f"⏭️ Skipping non-PDF file: {filename}")
            continue

        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_dir, f"{base_name}.txt")

        if os.path.exists(output_path):
            print(f"✅ Skipping existing file: {output_path}")
            continue

        print(f"📄 Processing: {filename}")
        with pdfplumber.open(os.path.join(input_dir, filename)) as pdf:
            raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(raw_text)

        print(f"✅ Saved to: {output_path}")

#==================================================================================================================================

#============================================== Extract Despachos =================================================================

def extract_text_between_labels(doc, start_label: str, end_label: str) -> str | None:
    start, end = None, None
    for ent in doc.ents:
        if ent.label_ == start_label and start is None:
            start = ent.end
        elif ent.label_ == end_label and start is not None:
            end = ent.start
            break
    return doc[start:end].text.strip() if start is not None and end is not None else None

def extract_all_despachos(extracted_doc, filename, folder_path) -> list:
    results = []
    current_secretaria = None

    des_ents = [ent for ent in extracted_doc.ents if ent.label_ == "DES"]
    secretaria_ents = [ent for ent in extracted_doc.ents if ent.label_ == "SECRETARIA"]
    all_ents = sorted(secretaria_ents + des_ents, key=lambda x: x.start)

    for i, ent in enumerate(all_ents):
        if ent.label_ == "SECRETARIA":
            current_secretaria = ent.text

        elif ent.label_ == "DES" and current_secretaria:
            start = ent.start
            end = all_ents[i + 1].start if i + 1 < len(all_ents) else len(extracted_doc)
            chunk = extracted_doc[start:end].text.replace(current_secretaria, "").strip()

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


def process_folder_separate_json(input_folder: str, output_folder: str):
    """
    Process each .txt file in input_folder, extract despachos, and
    save results in separate .json files inside output_folder.
    """
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            doc = nlp(text)
            despachos = extract_all_despachos(doc, filename, input_folder)

            if not despachos:
                print(f"⚠️ No despachos found in {filename}, skipping JSON.")
                continue

            json_name = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_folder, json_name)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(despachos, f, ensure_ascii=False, indent=2)

            print(f"✅ {len(despachos)} despachos saved to {output_path}")


#=======================================================================================================================