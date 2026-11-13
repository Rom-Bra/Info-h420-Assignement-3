import os
import pymupdf4llm


def convert_pdf_to_markdown(pdf_path: str) -> str:
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"No PDF at path '{pdf_path}'")

    markdown_content = pymupdf4llm.to_markdown(pdf_path)
    if not markdown_content or not markdown_content.strip():
        raise ValueError(f"PDF at '{pdf_path}' has no data")

    return markdown_content
