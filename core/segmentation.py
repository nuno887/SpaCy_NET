import os
import json
import re
from pathlib import Path

def process_all_txt_and_json(json_dir: str, txt_dir: str, root_output: str = 'DATA/RELATORIOS') -> None:
    """
    Splits each .txt by 'despacho' headers, creates a folder per despacho,
    saves full block and split sections, updates JSON with paths and fields.
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
            despacho_dir = file_dir / safe_name
            despacho_dir.mkdir(parents=True, exist_ok=True)

            # Save full block
            (despacho_dir / "completo.txt").write_text(segment_text, encoding="utf-8")

            # Split sections
            sections = split_despacho_sections(segment_text)
            (despacho_dir / "sumario.txt").write_text(sections["summary"], encoding="utf-8")
            (despacho_dir / "texto.txt").write_text(sections["texto"], encoding="utf-8")
            (despacho_dir / "anexo.txt").write_text(sections["anexo"], encoding="utf-8")

            for entry in data:
                if entry.get("despacho") == header:
                    relative_path = Path(root_output) / tfile.stem / safe_name

                    entry["path"] = str(relative_path).replace("\\", "/")
                    entry["summary_path"] = str(relative_path / "sumario.txt").replace("\\", "/")
                    entry["texto_path"] = str(relative_path / "texto.txt").replace("\\", "/")
                    entry["anexo_path"] = str(relative_path / "anexo.txt").replace("\\", "/")

                    # Remove inline large text fields to keep JSON clean
                    entry.pop("summary", None)
                    entry.pop("TEXT", None)
                    entry.pop("ANEXO", None)

                    print(f"[{tfile.name}] Updated paths for '{header}'")

        try:
            jfile.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"✅ JSON updated: {jfile.name}")
        except Exception as e:
            print(f"Error writing JSON {jfile}: {e}")

import re

def split_despacho_sections(segment_text):
    """
    Splits a despacho block strictly by:
    - 'Sumário:' (case-insensitive, requires colon)
    - 'Texto:'   (case-insensitive, requires colon)
    - 'ANEXO'    must be all caps, at line start, followed by newline
    Ensures section headers are not included inside the extracted text.
    """
    result = {"summary": "", "texto": "", "anexo": ""}

    # Patterns
    sum_pattern = re.compile(r'Sumário\s*:', re.IGNORECASE)
    text_pattern = re.compile(r'Texto\s*:', re.IGNORECASE)
    anexo_pattern = re.compile(r'(?m)^ANEXO\s*$', re.IGNORECASE)  # Must be at start of line, all caps

    sum_match = sum_pattern.search(segment_text)
    text_match = text_pattern.search(segment_text)
    anexo_match = anexo_pattern.search(segment_text)

    # Positions
    sum_start = sum_match.end() if sum_match else None
    text_start = text_match.start() if text_match else None
    text_content_start = text_match.end() if text_match else None
    anexo_start = anexo_match.start() if anexo_match else None
    anexo_content_start = anexo_match.end() if anexo_match else None

    # Extract summary
    if sum_start:
        next_start = text_start if text_start else (anexo_start if anexo_start else len(segment_text))
        result["summary"] = segment_text[sum_start:next_start].strip()

    # Extract texto
    if text_content_start:
        next_start = anexo_start if anexo_start else len(segment_text)
        result["texto"] = segment_text[text_content_start:next_start].strip()

    # Extract anexo
    if anexo_content_start:
        result["anexo"] = segment_text[anexo_content_start:].strip()

    return result
