import os
from pathlib import Path

from PyPDF2 import PdfWriter

from core import compress_pdf, merge_pdfs


def create_sample_pdf(path: Path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(path, "wb") as file:
        writer.write(file)


def test_merge_pdfs_creates_output(tmp_path: Path) -> None:
    input_one = tmp_path / "one.pdf"
    input_two = tmp_path / "two.pdf"
    create_sample_pdf(input_one)
    create_sample_pdf(input_two)

    merged_path = merge_pdfs([str(input_one), str(input_two)])
    assert Path(merged_path).exists()
    assert Path(merged_path).stat().st_size > 0


def test_compress_pdf_creates_output(tmp_path: Path) -> None:
    input_file = tmp_path / "source.pdf"
    create_sample_pdf(input_file)

    output_file = tmp_path / "source_compressed.pdf"
    compressed_path = compress_pdf(str(input_file), str(output_file))

    assert Path(compressed_path).exists()
    assert Path(compressed_path).stat().st_size > 0
