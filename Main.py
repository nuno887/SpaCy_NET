from SpaCy_Core import extract_text_from_pdf, process_folder_separate_json
import os

if __name__ == "__main__":
    # 📁 Adjust these paths to your folders
    pdf_input_folder = "DATA/PDF"          # Where your PDFs are stored
    text_output_folder = "DATA/TXT_UNPROCESSED"        # Where extracted .txt files will be saved
    json_output_folder = "DATA/JSON"  # Where final JSON file goes

    # Step 1: Convert PDFs to .txt
    print("\n=== Step 1: Extracting Text from PDFs ===")
    extract_text_from_pdf(pdf_input_folder, text_output_folder)

    # Step 2: Process .txt files to extract despachos
    print("\n=== Step 2: Processing Text Files for Despachos ===")
    process_folder_separate_json(text_output_folder, json_output_folder)

    print("\n✅ Process completed.")
