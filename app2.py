import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import numpy as np
import plotly.express as px

st.set_page_config(page_title="PDF-Template Ausschneider", layout="wide")
st.title("📐 Template aus PDF ausschneiden – mit Zoom & Weiterverarbeitung")

# --- PDF Upload ---
uploaded_pdf = st.file_uploader("📄 PDF hochladen", type=["pdf"])
if uploaded_pdf:
    pdf_bytes = uploaded_pdf.read()

    # --- PDF -> Bild (300 DPI) ---
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    mat = fitz.Matrix(300 / 72, 300 / 72)
    pix = page.get_pixmap(matrix=mat)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    original_image = image.copy()

    st.subheader("🔍 Zoombare Vorschau des Plans (volle Auflösung)")
    preview_array = np.array(image)  # kein Scaling
    scale = 1  # wichtig: keine Umrechnung nötig

    fig = px.imshow(preview_array)
    fig.update_layout(
        dragmode="zoom",
        height=int(image.height * 1.1),
        width=int(image.width * 1.1),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    st.plotly_chart(fig, use_container_width=False)

    # --- Koordinaten manuell eingeben ---
    st.subheader("✂️ Bereich auswählen – Koordinaten eingeben")
    col1, col2 = st.columns(2)
    with col1:
        x1 = st.number_input("🔹 x1", min_value=0, max_value=image.width, value=100)
        y1 = st.number_input("🔹 y1", min_value=0, max_value=image.height, value=100)
    with col2:
        x2 = st.number_input("🔸 x2", min_value=0, max_value=image.width, value=300)
        y2 = st.number_input("🔸 y2", min_value=0, max_value=image.height, value=300)

    # --- Ausschneiden & Weiterverarbeitung ---
    if st.button("💾 Ausschneiden & weiterverarbeiten"):
        left = int(min(x1, x2))
        top = int(min(y1, y2))
        right = int(max(x1, x2))
        bottom = int(max(y1, y2))

        cropped = original_image.crop((left, top, right, bottom))
        st.image(cropped, caption="📦 Ausgeschnittener Bereich", use_container_width=True)

        # Download
        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        st.download_button("⬇️ Template herunterladen", data=buf.getvalue(), file_name="template.png", mime="image/png")

        # Platzhalter für Weiterverarbeitung
        st.info("🔄 Weiterverarbeitung wäre hier möglich (z. B. Matching, GitHub-Upload).")
else:
    st.info("⬆️ Bitte lade eine PDF hoch, um zu starten.")









