import os
import pdfplumber
from pathlib import Path
import spacy
from spacy.pipeline import EntityRuler
import json
import re

from PATTERNS_SpaCy import COMPOSED_PATTERNS, PRIMARY_PATTERNS, HEADER_BLOCK_PATTERN


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

#==================== Eliminates a primeira and ultima pages do documento, elemina as datas(headers) de cada uma das paginas. ===========================

def process_txt_and_truncate(input_dir: str,
                             json_dir: str,
                             output_dir: str):
    """
    For each .txt file in input_dir:
      1. Load corresponding .json and get the 'despacho' field from the first record.
      2. Read the .txt file.
      3. Count how many times the despacho appears.
      4. If it appears at least twice, truncate the text before the 2nd occurrence.
      5. Save result to output_dir with same filename.
      6. Print filename, despacho, count, and action taken.

      Resume: Deletes the header of the pdf.
    """
    os.makedirs(output_dir, exist_ok=True)

    for filename in sorted(os.listdir(input_dir)):
        if not filename.lower().endswith(".txt"):
            continue

        base = os.path.splitext(filename)[0]
        json_path = os.path.join(json_dir, base + ".json")

        # 1) Load first despacho from JSON list
        try:
            with open(json_path, "r", encoding="utf-8") as jf:
                data = json.load(jf)

            if isinstance(data, list) and data and "despacho" in data[0]:
                key = data[0]["despacho"]
            else:
                key = None

        except (FileNotFoundError, json.JSONDecodeError):
            key = None

        print(f"\n== {filename} ==")
        if not key:
            print("  (no despacho key found in JSON)")
            continue
        print(f"  Despacho key: {key!r}")

        # 2) Read text
        txt_path = os.path.join(input_dir, filename)
        with open(txt_path, "r", encoding="utf-8") as tf:
            text = tf.read()

        # 3) Count occurrences
        count = text.count(key)
        print(f"  Occurrences: {count}")

        truncated = text
        truncated_flag = False

        # 4) Truncate before second occurrence if needed
        if count >= 2:
            first_pos = text.find(key)
            second_pos = text.find(key, first_pos + len(key))
            if second_pos != -1:
                truncated = text[second_pos:]
                truncated_flag = True

        # 5) Write out
        out_path = os.path.join(output_dir, filename)
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(truncated)

        # 6) Report
        status = "truncated" if truncated_flag else "unchanged"
        print(f"  Action: {status} (written to {out_path})")


def remove_text_after_last_header_block(directory_path: str, recurse: bool = False) -> None:
    """
    For each .txt file in the directory, finds the last occurrence of the header block
    (as defined by HEADER_BLOCK_PATTERN) and truncates the file content immediately
    after that block, removing any text that follows.
    """
    pattern = "**/*.txt" if recurse else "*.txt"
    for filepath in Path(directory_path).glob(pattern):
        if not filepath.is_file():
            continue
        text = filepath.read_text(encoding="utf-8")
        matches = list(HEADER_BLOCK_PATTERN.finditer(text))
        if not matches:
            continue  # no header block, leave file unchanged
        last_match = matches[-1]
        end_pos = last_match.end()
        truncated = text[:end_pos]
        # Overwrite file with truncated content
        filepath.write_text(truncated, encoding="utf-8")
        print(f"Truncated {filepath.name} after last header block.")

def remove_all_header_blocks(directory_path: str, recurse: bool = False) -> None:
    """
    For each .txt file in the directory, removes all occurrences of the header block
    (as defined by HEADER_BLOCK_PATTERN) from the file content.
    """
    pattern = "**/*.txt" if recurse else "*.txt"
    for filepath in Path(directory_path).glob(pattern):
        if not filepath.is_file():
            continue
        text = filepath.read_text(encoding="utf-8")
        # Remove all header blocks
        cleaned_text = HEADER_BLOCK_PATTERN.sub('', text)
        # Overwrite file if changes were made
        if cleaned_text != text:
            filepath.write_text(cleaned_text, encoding="utf-8")
            print(f"Removed all headers in {filepath.name}.")


#============================================================================================================================================

#=========================================


def process_all_txt_and_json(json_dir: str, txt_dir: str, root_output: str = 'DATA/RELATORIOS') -> None:
    """
    Pairs .json and .txt files by name, splits .txt by 'despacho' headers,
    updates JSON with 'path' only, saves segments to DATA/RELATORIOS.
    Does NOT touch 'summary', 'TEXT', or 'ANEXO'.
    """
    json_path = Path(json_dir)
    txt_path = Path(txt_dir)

    if not json_path.is_dir():
        raise ValueError(f"JSON directory not found: {json_dir}")
    if not txt_path.is_dir():
        raise ValueError(f"TXT directory not found: {txt_dir}")

    json_files = {p.stem: p for p in json_path.glob('*.json')}
    txt_files = {p.stem: p for p in txt_path.glob('*.txt')}
    common = set(json_files) & set(txt_files)

    if not common:
        print(f"No matching JSON and TXT files found between {json_dir} and {txt_dir}")
        return

    for stem in sorted(common):
        jfile = json_files[stem]
        tfile = txt_files[stem]

        try:
            data = json.loads(jfile.read_text(encoding='utf-8'))
            if not isinstance(data, list):
                print(f"Expected list in {jfile.name}, got {type(data).__name__}")
                continue
        except Exception as e:
            print(f"Error reading JSON {jfile}: {e}")
            continue

        content = tfile.read_text(encoding='utf-8')
        headers = [d.get("despacho") for d in data if "despacho" in d]
        escaped = [re.escape(h) for h in headers]
        pattern = re.compile(r'(?m)^(' + '|'.join(escaped) + r')')

        matches = list(pattern.finditer(content))
        if not matches:
            print(f"No despacho headers found in {tfile.name}")
            continue

        root_dir = Path(root_output)
        root_dir.mkdir(exist_ok=True)
        file_dir = root_dir / tfile.stem
        file_dir.mkdir(exist_ok=True)

        for idx, match in enumerate(matches):
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
            segment_text = content[start:end].strip()
            header = match.group(1)

            if not segment_text:
                continue

            safe_name = re.sub(r'[\\/:*?"<>| ]', '_', header)
            segment_path = file_dir / f"{safe_name}.txt"
            segment_path.write_text(segment_text, encoding='utf-8')

            for entry in data:
                if entry.get("despacho") == header:
                    relative_path = Path(root_output) / tfile.stem / f"{safe_name}.txt"
                    entry["path"] = str(relative_path).replace("\\", "/")
                    print(f"[{tfile.name}] Updated path for '{header}'")

        try:
            jfile.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"✅ JSON updated: {jfile.name}")
        except Exception as e:
            print(f"Error writing JSON {jfile}: {e}")

