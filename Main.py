import os
import shutil
from pipelines.tipo1_pipeline import run_pipeline as run_tipo1
from core.pdf_tools import extract_first_page_to_txt
from core.nlp_tools import has_despacho

if __name__ == "__main__":

    # === General Input Folders ===
    raw_pdf_folder = "DATA/PDF_INPUT"
    temp_txt_folder = "DATA/TEMP_TXT"
    pdf_others_folder = "DATA/PDF_OTHERS"
    pdf_despacho_folder = "DATA/PDF_01"

    os.makedirs(temp_txt_folder, exist_ok=True)
    os.makedirs(pdf_others_folder, exist_ok=True)
    os.makedirs(pdf_despacho_folder, exist_ok=True)

    print("\n=== Filtering PDFs by Despacho (copy only) ===")

    for filename in os.listdir(raw_pdf_folder):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(raw_pdf_folder, filename)
        txt_path = extract_first_page_to_txt(pdf_path, temp_txt_folder)

        if not txt_path or not os.path.exists(txt_path):
            continue

        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Decide folder based on presence of DES
        if has_despacho(text):
            dest_folder = pdf_despacho_folder
        else:
            dest_folder = pdf_others_folder

        shutil.copy2(pdf_path, os.path.join(dest_folder, filename))
        os.remove(txt_path)  # Clean up temporary .txt

        print(f"{'✔️' if dest_folder.endswith('PDF_01') else '⚠️'} {filename} → {dest_folder}")

    # === Pipeline 01 Variables ===
    txt_unprocessed_folder = "DATA/TXT_UNPROCESSED_01"
    txt_processed_folder = "DATA/TXT_PROCESSED_01"
    json_output_folder = "DATA/JSON"
    relatorios_folder = "DATA/RELATORIOS"

    print("\n=== Running Pipeline for PDF Tipo 1 ===")
    run_tipo1(
        pdf_input=pdf_despacho_folder,
        txt_unprocessed=txt_unprocessed_folder,
        txt_processed=txt_processed_folder,
        json_output=json_output_folder,
        relatorios=relatorios_folder
    )

    print("\n✅ Pipeline 01 completed successfully.")
