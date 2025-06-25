from core.pdf_tools import extract_text_from_pdf
from core.text_cleaning import process_txt_and_truncate, remove_text_after_last_header_block, remove_all_header_blocks
from core.nlp_tools import get_nlp, extract_all_despachos
from core.segmentation import process_all_txt_and_json

def run_pipeline(pdf_input, txt_unprocessed, txt_processed, json_output, relatorios):
    extract_text_from_pdf(pdf_input, txt_unprocessed)

    nlp = get_nlp()
    # Logic to process_folder_separate_json using `nlp` and `extract_all_despachos`

    process_txt_and_truncate(txt_unprocessed, json_output, txt_processed)
    remove_text_after_last_header_block(txt_processed, True)
    remove_all_header_blocks(txt_processed, True)
    process_all_txt_and_json(json_output, txt_processed, relatorios)
