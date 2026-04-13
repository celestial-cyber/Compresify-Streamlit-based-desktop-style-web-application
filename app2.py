import streamlit as st
from PyPDF2 import PdfMerger
import pikepdf
import tempfile
import os
import base64
from streamlit_sortables import sort_items

# -----------------------
# CONFIG (MUST BE FIRST)
# -----------------------
st.set_page_config(page_title="Compresify", page_icon="📄", layout="wide")

# -----------------------
# STYLE
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
# SIDEBAR
# -----------------------
st.sidebar.title("📄 Compresify")
option = st.sidebar.radio("Choose Tool", ["Merge PDFs", "Compress PDF"])
st.sidebar.caption("🚀 Built by Celestial V")

# -----------------------
# FUNCTIONS
# -----------------------

def merge_pdfs(files):
    merger = PdfMerger()
    for file in files:
        merger.append(file)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(temp.name)
    merger.close()
    return temp.name


def compress_pdf(input_path, level="medium"):
    output_path = input_path.replace(".pdf", "_compressed.pdf")

    with pikepdf.open(input_path) as pdf:
        pdf.save(
            output_path,
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            recompress_flate=True
        )

    return output_path


def show_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# -----------------------
# MERGE PDFs
# -----------------------

if option == "Merge PDFs":
    st.title("🔗 Merge PDFs")

    files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if files:
        file_names = [f.name for f in files]

        st.subheader("🔀 Reorder Files")
        sorted_names = sort_items(file_names)

        # Map sorted order back to files
        sorted_files = [next(f for f in files if f.name == name) for name in sorted_names]

        st.subheader("👀 Preview First File")
        show_pdf(sorted_files[0])

        output_name = st.text_input("Output name", "merged.pdf")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🚀 Merge"):
                with st.spinner("Merging..."):
                    merged_path = merge_pdfs(sorted_files)

                    with open(merged_path, "rb") as f:
                        st.success("Done!")
                        st.download_button("⬇ Download", f, file_name=output_name)

        with col2:
            if st.button("❌ Reset"):
                st.rerun()

# -----------------------
# COMPRESS PDFs
# -----------------------

elif option == "Compress PDF":
    st.title("🗜️ Compress PDFs")

    files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if files:
        level = st.selectbox("Compression Level", ["low", "medium", "high"])

        for file in files:
            st.subheader(f"📄 {file.name}")

            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp.write(file.read())
            temp.close()

            show_pdf(open(temp.name, "rb"))

            if st.button(f"⚡ Compress {file.name}"):
                with st.spinner("Compressing..."):
                    compressed = compress_pdf(temp.name, level)

                    original_size = os.path.getsize(temp.name) / 1024
                    compressed_size = os.path.getsize(compressed) / 1024

                    reduction = ((original_size - compressed_size) / original_size) * 100

                    st.write(f"📉 Original: {original_size:.2f} KB")
                    st.write(f"📦 Compressed: {compressed_size:.2f} KB")
                    st.write(f"🚀 Reduced: {reduction:.2f}%")

                    with open(compressed, "rb") as f:
                        st.download_button("⬇ Download", f, file_name=f"compressed_{file.name}")

# -----------------------
# FOOTER
# -----------------------
st.markdown("---")
st.caption("✨ Compresify | Fast • Smart • Efficient")