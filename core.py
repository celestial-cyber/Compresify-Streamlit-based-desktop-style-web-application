import tempfile
from pathlib import Path
from typing import Iterable

from PyPDF2 import PdfMerger
import pikepdf

MAX_UPLOAD_MB = 1024
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


def format_bytes(size: int) -> str:
    bytes_size = float(size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024 or unit == "TB":
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"


def save_uploaded_file(uploaded_file) -> str:
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{Path(uploaded_file.name).name}")
    try:
        uploaded_file.seek(0)
        temp_file.write(uploaded_file.read())
    finally:
        temp_file.close()
    return temp_file.name


def ensure_pdf_size(uploaded_file) -> bool:
    file_size = getattr(uploaded_file, "size", None)
    if file_size is not None and file_size > MAX_UPLOAD_BYTES:
        raise ValueError(f"Uploaded file exceeds the maximum allowed size of {MAX_UPLOAD_MB} MB.")
    return True


def merge_pdfs(file_paths: Iterable[str], output_filename: str = None) -> str:
    if output_filename is None:
        output_filename = "merged.pdf"

    output_path = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name)
    merger = PdfMerger()
    try:
        for path in file_paths:
            merger.append(str(path))
        merger.write(output_path)
    finally:
        merger.close()
    return str(output_path)


def compress_pdf(input_path: str, output_path: str = None) -> str:
    if output_path is None:
        output_path = str(Path(input_path).with_name(Path(input_path).stem + "_compressed.pdf"))

    with pikepdf.open(input_path) as pdf:
        pdf.save(
            output_path,
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            recompress_flate=True,
        )
    return output_path
