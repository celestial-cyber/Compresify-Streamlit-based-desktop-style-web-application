import streamlit as st
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import pikepdf
import tempfile
import os
import base64
from streamlit_sortables import sort_items
import fitz  # PyMuPDF
from PIL import Image

# -----------------------
# CONFIG
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
option = st.sidebar.radio("Choose Tool", ["Merge PDFs", "Compress PDF", "Modify PDF"])
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


def compress_pdf(input_path):
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


def render_page_as_image(pdf_path, page_number):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap()

    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

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
        sorted_files = [next(f for f in files if f.name == name) for name in sorted_names]

        st.subheader("👀 Preview")
        show_pdf(sorted_files[0])

        output_name = st.text_input("Output name", "merged.pdf")

        if st.button("🚀 Merge"):
            merged_path = merge_pdfs(sorted_files)

            with open(merged_path, "rb") as f:
                st.success("✅ Merge Complete!")
                st.download_button("⬇ Download", f, file_name=output_name)

# -----------------------
# COMPRESS PDFs
# -----------------------

elif option == "Compress PDF":
    st.title("🗜️ Compress PDFs")

    files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if files:
        for file in files:
            st.subheader(f"📄 {file.name}")

            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp.write(file.read())
            temp.close()

            show_pdf(open(temp.name, "rb"))

            if st.button(f"⚡ Compress {file.name}"):
                compressed = compress_pdf(temp.name)

                original = os.path.getsize(temp.name) / 1024
                new = os.path.getsize(compressed) / 1024
                reduction = ((original - new) / original) * 100

                st.write(f"📉 Original: {original:.2f} KB")
                st.write(f"📦 Compressed: {new:.2f} KB")
                st.write(f"🚀 Reduced: {reduction:.2f}%")

                with open(compressed, "rb") as f:
                    st.download_button("⬇ Download", f, file_name=f"compressed_{file.name}")

# -----------------------
# MODIFY PDF (WITH PREVIEW + DELETE)
# -----------------------

elif option == "Modify PDF":
    st.title("🛠 Modify PDF (Delete Pages)")

    file = st.file_uploader("Upload PDF", type="pdf")

    if file:
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp.write(file.read())
        temp.close()

        reader = PdfReader(temp.name)

        if "deleted_pages" not in st.session_state:
            st.session_state.deleted_pages = set()

        total_pages = len(reader.pages)
        st.write(f"📄 Total Pages: {total_pages}")

        st.subheader("📑 Page Preview")

        cols = st.columns(3)

        for i in range(total_pages):
            if i in st.session_state.deleted_pages:
                continue

            with cols[i % 3]:
                img = render_page_as_image(temp.name, i)
                st.image(img, caption=f"Page {i+1}", use_container_width=True)

                if st.button("🗑 Delete", key=f"del_{i}"):
                    st.session_state.deleted_pages.add(i)
                    st.rerun()

        if st.button("💾 Save Modified PDF"):
            writer = PdfWriter()

            for i in range(total_pages):
                if i not in st.session_state.deleted_pages:
                    writer.add_page(reader.pages[i])

            output_path = temp.name.replace(".pdf", "_modified.pdf")

            with open(output_path, "wb") as f:
                writer.write(f)

            st.success("✅ PDF Updated!")

            with open(output_path, "rb") as f:
                st.download_button("⬇ Download Modified PDF", f, file_name="modified.pdf")

# -----------------------
# FOOTER
# -----------------------
st.markdown("---")
st.caption("✨ Compresify | Fast • Smart • Efficient")