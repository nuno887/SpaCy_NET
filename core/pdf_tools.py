import fitz
import os

def extract_text_from_pdf(input_dir: str, output_dir: str, column_split_ratio: float = 0.4) -> None:
    """
    Extracts text from PDFs using PyMuPDF with sorting for two-column layouts.
    Skips last page. Supports adjustable column split ratio.
    """
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            base = os.path.splitext(filename)[0]
            out_path = os.path.join(output_dir, base + ".txt")

            if os.path.exists(out_path):
                continue

            doc = fitz.open(os.path.join(input_dir, filename))
            extracted_text = []

            total_pages = len(doc)

            for i, page in enumerate(doc):
                if i == total_pages - 1:
                    continue

                mid_x = page.rect.width * column_split_ratio
                left_lines = []
                right_lines = []

                text_dict = page.get_text("dict")

                for block in text_dict["blocks"]:
                    for line in block.get("lines", []):
                        x0s = [span["bbox"][0] for span in line["spans"]]
                        x0 = min(x0s)
                        y0 = round(line["bbox"][1], 1)

                        line_text = "".join(span["text"] for span in line["spans"]).strip()
                        if not line_text or line_text.isspace():
                            continue

                        if x0 < mid_x:
                            left_lines.append((y0, x0, line_text))
                        else:
                            right_lines.append((y0, x0, line_text))

                left_lines.sort(key=lambda l: (l[0], l[1]))
                right_lines.sort(key=lambda l: (l[0], l[1]))

                ordered_text = [text for _, _, text in left_lines] + [text for _, _, text in right_lines]

                extracted_text.append("\n".join(ordered_text))

            full_text = "\n".join(extracted_text).strip()

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            doc.close()
            print(f"✅ Saved to: {out_path}")
