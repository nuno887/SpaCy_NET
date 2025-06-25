import os
import pdfplumber

def extract_text_from_pdf(input_dir: str, output_dir: str) -> None:
    """
    Extract text from all PDFs to .txt files.
    """
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            base = os.path.splitext(filename)[0]
            out_path = os.path.join(output_dir, base + ".txt")
            if not os.path.exists(out_path):
                with pdfplumber.open(os.path.join(input_dir, filename)) as pdf:
                    raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(raw_text)
