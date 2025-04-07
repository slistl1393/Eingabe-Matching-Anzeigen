import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import streamlit_image_coordinates

st.set_page_config(page_title="Template-Ausschneider", layout="wide")
st.title("📐 Template aus PDF ausschneiden")

def convert_pdf_to_image(pdf_bytes, dpi=200, page_number=0):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_number)
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

uploaded_pdf = st.file_uploader("📄 PDF hochladen", type=["pdf"])
if uploaded_pdf:
    pdf_bytes = uploaded_pdf.read()
    image_full = convert_pdf_to_image(pdf_bytes).convert("RGB")

    zoom = 2
    preview = image_full.resize((image_full.width * zoom, image_full.height * zoom))

    st.subheader("🖼️ Vorschau – klicke zwei Punkte")
    coords = streamlit_image_coordinates.streamlit_image_coordinates(preview, key="clicks")

    if coords:
        st.write("📍 Gewählte Punkte:", coords)

    if coords and len(coords) >= 2:
        st.success("✅ Zwei Punkte gesetzt")

        x1, y1 = coords[0]["x"], coords[0]["y"]
        x2, y2 = coords[1]["x"], coords[1]["y"]

        left, top = int(min(x1, x2) / zoom), int(min(y1, y2) / zoom)
        right, bottom = int(max(x1, x2) / zoom), int(max(y1, y2) / zoom)

        cropped = image_full.crop((left, top, right, bottom))
        st.image(cropped, caption="Ausschnitt", use_container_width=True)

        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        st.download_button("💾 Template speichern", buf.getvalue(), "template.png", mime="image/png")
    elif coords:
        st.info("🧭 Bitte zwei Punkte setzen (oben links & unten rechts).")
else:
    st.info("⬆️ Lade eine PDF-Datei hoch.")








