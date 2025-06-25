import os
import json
from pathlib import Path
from patterns.patterns_spacy import HEADER_BLOCK_PATTERN

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