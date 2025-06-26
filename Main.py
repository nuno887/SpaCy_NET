from pipelines.tipo1_pipeline import run_pipeline as run_tipo1
from core.pdf_tools import extract_first_page_to_txt
if __name__ == "__main__":













    # Folder structure setup
    pdf_input_folder = "DATA/PDF_01"
    txt_unprocessed_folder = "DATA/TXT_UNPROCESSED_01"
    txt_processed_folder = "DATA/TXT_PROCESSED_01"
    json_output_folder = "DATA/JSON"
    relatorios_folder = "DATA/RELATORIOS"

    print("\n=== Running Pipeline for PDF Tipo 1 ===")
    run_tipo1(
        pdf_input=pdf_input_folder,
        txt_unprocessed=txt_unprocessed_folder,
        txt_processed=txt_processed_folder,
        json_output=json_output_folder,
        relatorios=relatorios_folder
    )

    print("\n✅ Pipeline completed successfully.")
