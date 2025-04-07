import streamlit as st
import fitz
from PIL import Image, ImageDraw
import io
import streamlit_image_coordinates

import streamlit as st
import fitz
from PIL import Image, ImageDraw
import io
import streamlit_image_coordinates

st.set_page_config(page_title="PDF-Plan ausschneiden", layout="wide")
st.title("📐 PDF-Plan ausschneiden mit Klick")

# --- PDF -> Bild ---
def convert_pdf_to_image(pdf_bytes, dpi=150):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# --- Upload ---
uploaded_pdf = st.file_uploader("📄 PDF hochladen", type=["pdf"])
if uploaded_pdf:
    pdf_bytes = uploaded_pdf.read()
    image = convert_pdf_to_image(pdf_bytes).convert("RGB")

    # Vorschau skalieren (z. B. 1200px Breite – Qualität zweitrangig)
    preview_width = 1200
    scale = preview_width / image.width
    preview = image.resize((int(image.width * scale), int(image.height * scale)))

    st.subheader("🖱️ Klicke zwei Punkte in der Vorschau")
    coords = streamlit_image_coordinates.streamlit_image_coordinates(preview, key="clicks")

    if coords:
        # Punkte markieren
        img_copy = preview.copy()
        draw = ImageDraw.Draw(img_copy)
        for p in coords:
            x = p["x"]
            y = p["y"]
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="red", outline="white", width=2)
        st.image(img_copy, caption="📍 Geklickte Punkte", use_container_width=True)
    else:
        st.image(preview, caption="🖼️ Vorschau", use_container_width=True)

    if coords and len(coords) >= 2:
        st.success("✅ Zwei Punkte gesetzt – Ausschnitt wird erstellt")

        x1 = coords[0]["x"]
        y1 = coords[0]["y"]
        x2 = coords[1]["x"]
        y2 = coords[1]["y"]

        left = int(min(x1, x2) / scale)
        top = int(min(y1, y2) / scale)
        right = int(max(x1, x2) / scale)
        bottom = int(max(y1, y2) / scale)

        cropped = image.crop((left, top, right, bottom))
        st.subheader("📦 Ausgeschnittener Bereich")
        st.image(cropped, caption="Dein Ausschnitt", use_container_width=True)

        # Download
        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        st.download_button("💾 Template speichern", buf.getvalue(), "template.png", mime="image/png")
    elif coords:
        st.info("ℹ️ Bitte zwei Punkte setzen.")
else:
    st.info("⬆️ Lade eine PDF-Datei hoch.")








