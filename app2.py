import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import streamlit_image_coordinates

st.set_page_config(page_title="Template-Ausschneider", layout="wide")
st.title("📐 Template ausschneiden aus PDF")

# --- PDF zu Bild konvertieren ---
def convert_pdf_to_image(pdf_bytes, dpi=200, page_number=0):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_number)
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

# --- Upload PDF ---
uploaded_pdf = st.file_uploader("📄 PDF hochladen", type=["pdf"])
if uploaded_pdf:
    dpi = 200
    pdf_bytes = uploaded_pdf.read()
    image_full = convert_pdf_to_image(pdf_bytes, dpi=dpi).convert("RGB")

    # Vorschau erzeugen (vergrößert, klickbar)
    zoom_factor = 2
    preview = image_full.resize((image_full.width * zoom_factor, image_full.height * zoom_factor))

    st.subheader("🖼️ Vorschau (klicke 2 Punkte)")
    coords = streamlit_image_coordinates.streamlit_image_coordinates(preview, key="clicks")

    if coords:
        st.write("📍 Gewählte Koordinaten:", coords)

    # Wenn 2 Punkte gesetzt wurden
    if coords and len(coords) >= 2:
        st.success("✅ Zwei Punkte gesetzt")

        # Koordinaten zurückskalieren
        x1, y1 = coords[0]["x"], coords[0]["y"]
        x2, y2 = coords[1]["x"], coords[1]["y"]
        left, top = int(min(x1, x2) / zoom_factor), int(min(y1, y2) / zoom_factor)
        right, bottom = int(max(x1, x2) / zoom_factor), int(max(y1, y2) / zoom_factor)

        cropped = image_full.crop((left, top, right, bottom))
        st.image(cropped, caption="Ausgeschnittener Bereich", use_container_width=True)

        # Download-Button
        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        st.download_button("💾 Template herunterladen", buf.getvalue(), "template.png", mime="image/png")
    elif coords:
        st.info("ℹ️ Bitte zwei Punkte setzen: oben links und unten rechts.")
else:
    st.info("⬆️ Bitte lade eine PDF-Datei hoch.")







