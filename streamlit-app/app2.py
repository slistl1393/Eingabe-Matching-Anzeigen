import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import numpy as np
import plotly.express as px

st.set_page_config(page_title="PDF-Template Ausschneider", layout="wide")
st.title("📐 Verzeichnis aus PDF ausschneiden")

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

    st.subheader("✂️ Verzeichnisbereich auswählen – Koordinaten eingeben")
    col1, col2 = st.columns(2)
    with col1:
        x1 = st.number_input("🔹 x1", min_value=0, max_value=image.width, value=100)
        y1 = st.number_input("🔹 y1", min_value=0, max_value=image.height, value=100)
    with col2:
        x2 = st.number_input("🔸 x2", min_value=0, max_value=image.width, value=300)
        y2 = st.number_input("🔸 y2", min_value=0, max_value=image.height, value=300)

    # --- Vorschau mit Markern ---
    st.subheader("🔍 Zoombare Vorschau des Plans mit Auswahlpunkten")
    preview_array = np.array(image)
    fig = px.imshow(preview_array, binary_format='png')
    fig.update_layout(
        dragmode="zoom",
        height=850,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    if (x1 != x2) and (y1 != y2):
        fig.add_scatter(
            x=[x1, x2],
            y=[y1, y2],
            mode="markers",
            marker=dict(size=10, color="red"),
            name="Auswahlpunkte"
        )
    else:
        st.warning("⚠️ Setze bitte zwei unterschiedliche Punkte für die Auswahl.")

    st.plotly_chart(fig, use_container_width=True)

    # --- Ausschneiden & Weiterverarbeitung ---
    if st.button("💾 Verzeichnis & Plan als PNG exportieren"):
        left = int(min(x1, x2))
        top = int(min(y1, y2))
        right = int(max(x1, x2))
        bottom = int(max(y1, y2))

        if left == right or top == bottom:
            st.error("❌ Ungültige Auswahl – x1 ≠ x2 und y1 ≠ y2 erforderlich.")
        else:
            cropped = original_image.crop((left, top, right, bottom))
            st.subheader("📦 Ausgeschnittener Bereich")
            st.image(cropped, caption="Dein Verzeichnis", use_container_width=True)

            # Bilder in Session State speichern
            plan_buf = io.BytesIO()
            original_image.save(plan_buf, format="PNG")
            st.session_state["plan_image"] = plan_buf.getvalue()

            verzeichnis_buf = io.BytesIO()
            cropped.save(verzeichnis_buf, format="PNG")
            st.session_state["verzeichnis_image"] = verzeichnis_buf.getvalue()

            st.success("✅ Bilder erstellt – jetzt kannst du sie unten herunterladen.")

    # --- Download Buttons ---
    if "plan_image" in st.session_state and "verzeichnis_image" in st.session_state:
        st.subheader("⬇️ Download")
        st.download_button("⬇️ Plan herunterladen", data=st.session_state["plan_image"],
                           file_name="plan.png", mime="image/png")
        st.download_button("⬇️ Verzeichnis herunterladen", data=st.session_state["verzeichnis_image"],
                           file_name="verzeichnis.png", mime="image/png")
else:
    st.info("⬆️ Bitte lade eine PDF hoch, um zu starten.")












