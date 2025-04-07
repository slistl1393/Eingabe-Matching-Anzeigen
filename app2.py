import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io
import streamlit_image_coordinates

st.set_page_config(page_title="PDF-Ausschnitt mit Zoom & Klick", layout="wide")
st.title("📐 PDF-Plan ausschneiden mit Zoom und Klickvorschau")

# --- Hilfsfunktion zur PDF-Konvertierung ---
def convert_pdf_to_image(pdf_bytes, dpi=200, page_number=0):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_number)
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# --- Upload ---
uploaded_pdf = st.file_uploader("📄 Lade eine PDF-Datei hoch", type=["pdf"])
if uploaded_pdf:
    raw_pdf = uploaded_pdf.read()
    image_full = convert_pdf_to_image(raw_pdf).convert("RGB")

    # --- Zoomfaktor wählbar ---
    zoom_factor = st.slider("🔍 Zoomfaktor für Vorschau", min_value=1, max_value=4, value=2)
    preview = image_full.resize(
        (image_full.width * zoom_factor, image_full.height * zoom_factor)
    )

    # --- Koordinaten auswählen ---
    st.subheader("🖱️ Klicke zwei Punkte in der Vorschau (oben links & unten rechts)")
    coords = streamlit_image_coordinates.streamlit_image_coordinates(preview, key="clicks")

    # --- Punkte visuell markieren ---
    if coords:
        preview_with_points = preview.copy()
        draw = ImageDraw.Draw(preview_with_points)
        for point in coords:
            x, y = point["x"], point["y"]
            r = 6
            draw.ellipse((x - r, y - r, x + r, y + r), fill="red", outline="white", width=2)
        st.image(preview_with_points, caption="🖼️ Vorschau mit Punkten", use_container_width=True)
    else:
        st.image(preview, caption="🖼️ Vorschau", use_container_width=True)

    # --- Ausschneiden, wenn 2 Punkte gesetzt ---
    if coords and len(coords) >= 2:
        st.success("✅ Zwei Punkte gesetzt – Bereich wird ausgeschnitten")
        x1, y1 = coords[0]["x"], coords[0]["y"]
        x2, y2 = coords[1]["x"], coords[1]["y"]

        # Rückskalierung auf Originalgröße
        left = int(min(x1, x2) / zoom_factor)
        top = int(min(y1, y2) / zoom_factor)
        right = int(max(x1, x2) / zoom_factor)
        bottom = int(max(y1, y2) / zoom_factor)

        cropped = image_full.crop((left, top, right, bottom))
        st.image(cropped, caption="📦 Ausgeschnittener Bereich", use_container_width=True)

        # Download
        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        st.download_button("💾 Template speichern", buf.getvalue(), "template.png", mime="image/png")
    elif coords:
        st.info("ℹ️ Bitte noch einen zweiten Punkt setzen.")
else:
    st.info("⬆️ Lade eine PDF-Datei hoch, um zu starten.")









