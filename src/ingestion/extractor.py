from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def save_text(text: str, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raw_pdf = "data/raw/clt.pdf"
    output_txt = "data/processed/clt.txt"
    text = extract_text_from_pdf(raw_pdf)
    save_text(text, output_txt)
    print(f"Extracted {len(text)} characters -> {output_txt}")
