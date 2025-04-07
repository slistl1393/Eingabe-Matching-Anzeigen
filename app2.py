import streamlit as st
import fitz
from PIL import Image, ImageDraw
import io
import streamlit_image_coordinates
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Zoom & Klick Vorschau", layout="wide")
st.title("📐 PDF-Plan ausschneiden mit Zoom + Koordinaten")

# --- PDF zu Bild ---
def convert_pdf_to_image(pdf_bytes, dpi=200):
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

    # Vorschau mit Zoom (nur visuell)
    st.subheader("🔍 Zoombare Vorschau")
    fig = px.imshow(np.array(image))
    fig.update_layout(height=800)
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    # Vorschau zum Klicken
    st.subheader("🖱️ Auswahl: Klicke zwei Punkte für Ausschnitt")
    click_preview = image.resize((1000, int(1000 * image.height / image.width)))
    coords = streamlit_image_coordinates.streamlit_image_coordinates(click_preview, key="clicks")

    if coords:
        # Punkte visuell zeigen
        img_copy = click_preview.copy()
        draw = ImageDraw.Draw(img_copy)
        for p in coords:
            draw.ellipse((p["x"]-5, p["y"]-5, p["x"]+5, p["y"]+5), fill="red", outline="white", width=2)
        st.image(img_copy, caption="📍 Geklickte Punkte", use_container_width=True)

    if coords and len(coords) >= 2:
        scale = image.width / click_preview.width
        x1, y1 = coords[0]["x"], coords[0]["y"]
        x2, y2 = coords[1]["x"], coords[1]["y"]
        left, top = int(min(x1, x2) * scale), int(min(y1, y2) * scale)
        right, bottom = int(max(x1, x2) * scale), int(max(y1, y2) * scale)

        cropped = image.crop((left, top, right, bottom))
        st.subheader("📦 Ausgeschnittener Bereich")
        st.image(cropped, caption="Ausschnitt", use_container_width=True)

        # Download
        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        st.download_button("💾 Ausschnitt speichern", buf.getvalue(), "template.png", mime="image/png")
    elif coords:
        st.info("⚠️ Bitte zwei Punkte setzen.")
else:
    st.info("⬆️ Bitte lade eine PDF hoch.")









