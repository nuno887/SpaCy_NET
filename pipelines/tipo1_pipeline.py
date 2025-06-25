import os
from core.pdf_tools import extract_text_from_pdf
from core.text_cleaning import process_txt_and_truncate, remove_text_after_last_header_block, remove_all_header_blocks
from core.segmentation import process_all_txt_and_json
from core.json_tools import extract_and_save_despachos

def run_pipeline(pdf_input, txt_unprocessed, txt_processed, json_output, relatorios):
    extract_text_from_pdf(pdf_input, txt_unprocessed)
    extract_and_save_despachos(txt_unprocessed, json_output)
    process_txt_and_truncate(txt_unprocessed, json_output, txt_processed)
    remove_text_after_last_header_block(txt_processed, recurse=True)
    remove_all_header_blocks(txt_processed, recurse=True)
    process_all_txt_and_json(json_output, txt_processed, relatorios)
