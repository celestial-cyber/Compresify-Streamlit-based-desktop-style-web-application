import os
from pathlib import Path
from typing import List

import streamlit as st

from core import (
    MAX_UPLOAD_MB,
    compress_pdf,
    ensure_pdf_size,
    format_bytes,
    merge_pdfs,
    save_uploaded_file,
)

st.set_page_config(page_title="Compresify", page_icon="📄", layout="wide")

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("📄 Compresify")
option = st.sidebar.radio("Choose Tool", ["Merge PDFs", "Compress PDF"])
st.sidebar.markdown("---")
st.sidebar.caption(f"✅ Supports uploads up to {MAX_UPLOAD_MB} MB")


def cleanup_temp_files(files: List[str]) -> None:
    for path in files:
        try:
            os.remove(path)
        except OSError:
            pass


if option == "Merge PDFs":
    st.title("🔗 Merge PDFs")
    st.info("Upload multiple PDFs and merge them into a single document. Supports uploads up to 1 GB.")

    files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    if files:
        valid_files = []
        for file in files:
            file_size = getattr(file, "size", None)
            if file_size and file_size > MAX_UPLOAD_MB * 1024 * 1024:
                st.error(f"'{file.name}' is larger than {MAX_UPLOAD_MB} MB and cannot be processed.")
            else:
                valid_files.append(file)

        if valid_files:
            st.subheader("📂 Uploaded Files")
            for file in valid_files:
                file_size = getattr(file, "size", None)
                st.write(f"{file.name} — {format_bytes(file_size) if file_size else 'Size unknown'}")

            output_name = st.text_input("Output file name", "merged.pdf")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Merge"):
                    with st.spinner("Merging PDFs..."):
                        temp_files = []
                        merged_file = None
                        try:
                            for uploaded_file in valid_files:
                                ensure_pdf_size(uploaded_file)
                                temp_files.append(save_uploaded_file(uploaded_file))

                            merged_file = merge_pdfs(temp_files)
                            with open(merged_file, "rb") as file_data:
                                st.success("✅ Merge complete.")
                                st.download_button(
                                    label="⬇ Download Merged PDF",
                                    data=file_data,
                                    file_name=output_name,
                                    mime="application/pdf",
                                )
                        except Exception as error:
                            st.error(f"Merge failed: {error}")
                        finally:
                            cleanup_temp_files(temp_files)
                            if merged_file:
                                cleanup_temp_files([merged_file])

            with col2:
                if st.button("❌ Reset"):
                    st.experimental_rerun()

elif option == "Compress PDF":
    st.title("🗜️ Compress PDF")
    st.info("Upload a PDF and create a compressed version. Supports uploads up to 1 GB.")

    file = st.file_uploader("Upload a PDF", type="pdf")
    if file:
        file_size = getattr(file, "size", None)
        st.write(f"📄 {file.name} — {format_bytes(file_size) if file_size else 'Size unknown'}")

        output_name = st.text_input("Output file name", "compressed.pdf")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("⚡ Compress"):
                with st.spinner("Compressing PDF..."):
                    temp_path = None
                    compressed_path = None
                    try:
                        ensure_pdf_size(file)
                        temp_path = save_uploaded_file(file)
                        compressed_path = compress_pdf(temp_path)

                        original_size = Path(temp_path).stat().st_size
                        compressed_size = Path(compressed_path).stat().st_size
                        reduction = ((original_size - compressed_size) / original_size) * 100

                        st.write(f"📉 Original size: {format_bytes(original_size)}")
                        st.write(f"📦 Compressed size: {format_bytes(compressed_size)}")
                        st.write(f"🚀 Reduced by: {reduction:.2f}%")

                        with open(compressed_path, "rb") as file_data:
                            st.success("✅ Compression complete.")
                            st.download_button(
                                label="⬇ Download Compressed PDF",
                                data=file_data,
                                file_name=output_name,
                                mime="application/pdf",
                            )
                    except Exception as error:
                        st.error(f"Compression failed: {error}")
                    finally:
                        cleanup_temp_files([temp_path] if temp_path else [])
                        cleanup_temp_files([compressed_path] if compressed_path else [])

        with col2:
            if st.button("❌ Reset"):
                st.experimental_rerun()

st.markdown("---")
st.caption("🚀 Compresify | Built for production uploads up to 1 GB")
