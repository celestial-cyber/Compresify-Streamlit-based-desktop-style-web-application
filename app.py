import streamlit as st
from PyPDF2 import PdfMerger
import pikepdf
import tempfile
import os

# -----------------------
# MUST BE FIRST STREAMLIT COMMAND
# -----------------------
st.set_page_config(
    page_title="Compresify",
    page_icon="📄",
    layout="wide"
)

# -----------------------
# Custom CSS (AFTER config)
# -----------------------
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

# -----------------------
# Sidebar
# -----------------------
st.sidebar.title("📄 Compresify")
option = st.sidebar.radio("Choose Tool", ["Merge PDFs", "Compress PDF"])

st.sidebar.markdown("---")
st.sidebar.caption("✨ Built by Celestial V")

# -----------------------
# Functions
# -----------------------

def merge_pdfs(files):
    merger = PdfMerger()
    for file in files:
        merger.append(file)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(temp_file.name)
    merger.close()

    return temp_file.name


def compress_pdf(input_path, level="medium"):
    output_path = input_path.replace(".pdf", "_compressed.pdf")

    # Compression settings
    if level == "low":
        quality = 80
    elif level == "medium":
        quality = 50
    else:  # high
        quality = 30

    with pikepdf.open(input_path) as pdf:
        pdf.save(
            output_path,
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            recompress_flate=True
        )

    return output_path

# -----------------------
# Merge PDFs UI
# -----------------------

if option == "Merge PDFs":
    st.title("🔗 Merge PDFs")

    files = st.file_uploader(
        "Upload PDF files",
        type="pdf",
        accept_multiple_files=True
    )

    if files:
        st.subheader("📂 Uploaded Files")

        for i, file in enumerate(files, 1):
            st.write(f"{i}. {file.name}")

        output_name = st.text_input("Output file name", "merged.pdf")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🚀 Merge"):
                with st.spinner("Merging PDFs..."):
                    merged_path = merge_pdfs(files)

                    with open(merged_path, "rb") as f:
                        st.success("✅ Merge Complete!")
                        st.download_button(
                            label="⬇ Download Merged PDF",
                            data=f,
                            file_name=output_name,
                            mime="application/pdf"
                        )

        with col2:
            if st.button("❌ Reset"):
                st.rerun()

# -----------------------
# Compress PDF UI
# -----------------------

elif option == "Compress PDF":
    st.title("🗜️ Compress PDF")

    file = st.file_uploader("Upload a PDF", type="pdf")

    if file:
        st.write(f"📄 {file.name}")

        output_name = st.text_input("Output file name", "compressed.pdf")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⚡ Compress"):
                with st.spinner("Compressing PDF..."):
                    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    temp_input.write(file.read())
                    temp_input.close()

                    compressed_path = compress_pdf(temp_input.name)

                    with open(compressed_path, "rb") as f:
                        st.success("✅ Compression Complete!")
                        st.download_button(
                            label="⬇ Download Compressed PDF",
                            data=f,
                            file_name=output_name,
                            mime="application/pdf"
                        )

        with col2:
            if st.button("❌ Reset"):
                st.rerun()

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.caption("🚀 Compresify | Fast • Simple • Efficient")