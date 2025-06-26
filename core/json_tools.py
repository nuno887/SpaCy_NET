import os
import json
from pathlib import Path
from core.nlp_tools import get_nlp, extract_all_despachos

def extract_and_save_despachos(txt_dir, json_output_dir):
    """
    Processes .txt files with SpaCy to extract despachos.
    Saves results as individual .json files.
    """
    nlp = get_nlp()
    os.makedirs(json_output_dir, exist_ok=True)

    for filename in os.listdir(txt_dir):
        if filename.endswith(".txt"):
            txt_path = os.path.join(txt_dir, filename)
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()

            doc = nlp(text)

            print(f"\nEntities in {filename}:")
            for ent in doc.ents:
                print(f"  {ent.label_}: {ent.text}")

            despachos = extract_all_despachos(doc, filename, txt_dir)
            print(f"Found {len(despachos)} despachos in {filename}")

            if despachos:
                json_path = os.path.join(json_output_dir, Path(filename).stem + ".json")
                with open(json_path, "w", encoding="utf-8") as jf:
                    json.dump(despachos, jf, ensure_ascii=False, indent=2)
                print(f"✅ JSON saved: {json_path}")
            else:
                print(f"⚠️ No despachos found in {filename}, skipping JSON.")



