from SpaCy_Core import extract_text_from_pdf, process_folder_separate_json, process_txt_and_truncate, remove_text_after_last_header_block, remove_all_header_blocks
import os

if __name__ == "__main__":
    # 📁 Adjust these paths to your folders
    pdf_input_folder = "DATA/PDF"          # Where your PDFs are stored
    text_unprocessed_folder = "DATA/TXT_UNPROCESSED"        # Where extracted .txt files will be saved
    text_processed_folder = "DATA/TXT_PROCESSED"
    json_output_folder = "DATA/JSON"  # Where final JSON file goes

    # Step 1: Convert PDFs to .txt
    print("\n=== Step 1: Extracting Text from PDFs ===")
    extract_text_from_pdf(pdf_input_folder, text_unprocessed_folder)

    # Step 2: Process .txt files to extract despachos
    print("\n=== Step 2: Processing Text Files for Despachos ===")
    process_folder_separate_json(text_unprocessed_folder, json_output_folder)

    # Step 3: Deletes the first page of the doc
    process_txt_and_truncate(text_unprocessed_folder, json_output_folder, text_processed_folder)

    remove_text_after_last_header_block(text_processed_folder, True)

    remove_all_header_blocks(text_processed_folder, True)

    print("\n✅ Process completed.")
