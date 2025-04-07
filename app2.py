import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import io
import base64
import pandas as pd
import plotly.express as px
import streamlit_image_coordinates

st.set_page_config(page_title="PDF-Bauteilerkennung", layout="wide")
st.title("📐 PDF-Plan hochladen, Template ausschneiden und auswerten")

# --- Hilfsfunktion zur PDF-Konvertierung ---
def convert_pdf_page_to_image(pdf_bytes, dpi=150, page_number=0):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_number)
    zoom = dpi / 72  # 72 ist PDF-Standard-DPI
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

# --- PDF Upload ---
uploaded_pdf = st.file_uploader("📄 Lade deinen Plan als PDF hoch", type=["pdf"])

if uploaded_pdf:
    st.subheader("⚙️ Einstellungen")
    dpi = st.slider("Wähle die DPI für die PDF-Konvertierung", min_value=100, max_value=400, value=300, step=50)

    # PDF lesen und vorbereiten
    raw_pdf = uploaded_pdf.read()
    pdf_bytes = io.BytesIO(raw_pdf)
    doc = fitz.open(stream=raw_pdf, filetype="pdf")
    num_pages = len(doc)
    page_num = st.number_input("Seitenzahl wählen", min_value=1, max_value=num_pages, value=1)

    # --- PDF -> Bild in voller Auflösung ---
    image_pil_full = convert_pdf_page_to_image(pdf_bytes, dpi=dpi, page_number=page_num - 1).convert("RGB")

    # --- Vorschaubild vorbereiten ---
    zoom_factor = 2  # Vorschau wird 2x größer dargestellt
    image_pil = image_pil_full.resize(
        (image_pil_full.width * zoom_factor, image_pil_full.height * zoom_factor)
    )

    st.subheader(f"🖼️ Vorschau – Seite {page_num} (DPI: {dpi})")
    coords = streamlit_image_coordinates.streamlit_image_coordinates(
        image_pil,
        key="template_coords"
    )

    if coords:
        st.write("📍 Gewählte Koordinaten:", coords)

    # --- Gesamtplan als PNG speichern ---
    buffered = io.BytesIO()
    image_pil.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    st.download_button(
        label="💾 Gesamtplan als PNG speichern",
        data=img_bytes,
        file_name="plan.png",
        mime="image/png"
    )

    # --- Template ausschneiden nach 2 Klicks ---
    if coords is not None and len(coords) >= 2:
        st.success("✅ Zwei Punkte gesetzt, Ausschnitt wird erstellt.")

        x1, y1 = coords[0]["x"], coords[0]["y"]
        x2, y2 = coords[1]["x"], coords[1]["y"]
        left, top = int(min(x1, x2) / zoom_factor), int(min(y1, y2) / zoom_factor)
        right, bottom = int(max(x1, x2) / zoom_factor), int(max(y1, y2) / zoom_factor)

        cropped = image_pil_full.crop((left, top, right, bottom))
        st.subheader("📦 Ausgeschnittenes Template")
        st.image(cropped, caption="Dein Template-Ausschnitt", use_container_width=True)

        # Download-Button für Template
        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="💾 Template als PNG speichern",
            data=byte_im,
            file_name="template.png",
            mime="image/png"
        )

        st.success("✅ Template erfolgreich ausgeschnitten!")
        st.markdown("---")

        st.info("🧠 Nächster Schritt: Template Matching via externem Backend")
        if st.button("🔄 Externes Matching starten"):
            st.warning("🔹 Hier würde ein Request an das Backend erfolgen (z. B. via FastAPI).")
    elif coords is not None:
        st.info("ℹ️ Bitte zwei Punkte in der Vorschau setzen: oben links & unten rechts.")
else:
    st.info("⬆️ Bitte lade zunächst eine PDF-Datei hoch.")






