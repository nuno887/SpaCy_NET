import os
import json
import re
from pathlib import Path

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