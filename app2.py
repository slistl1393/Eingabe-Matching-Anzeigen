import streamlit as st
import fitz  # PyMuPDF
import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="PDF Template Ausschneiden", layout="wide")
st.title("📐 Template per Maus auswählen und ausschneiden")

# --- PDF Upload ---
uploaded_pdf = st.file_uploader("📄 PDF hochladen", type=["pdf"])
if uploaded_pdf:
    pdf_bytes = uploaded_pdf.read()

    # PDF -> Bild (200 DPI für Qualität & Performance)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    mat = fitz.Matrix(200 / 72, 200 / 72)
    pix = page.get_pixmap(matrix=mat)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    original_image = image.copy()

    st.subheader("🖱️ Ziehe ein Rechteck über den gewünschten Bereich:")

    # --- Canvas für Rechteckauswahl ---
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=3,
        stroke_color="#FF0000",
        background_image=image,
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="rect",
        key="canvas"
    )

    # --- Rechteck ausgewählt?
    if canvas_result.json_data and canvas_result.json_data["objects"]:
        obj = canvas_result.json_data["objects"][0]
        left = int(obj["left"])
        top = int(obj["top"])
        width = int(obj["width"])
        height = int(obj["height"])
        right = left + width
        bottom = top + height

        # --- Bildausschnitt erzeugen
        cropped = original_image.crop((left, top, right, bottom))
        st.subheader("📦 Ausgeschnittener Bereich")
        st.image(cropped, caption="Dein Template", use_container_width=True)

        # --- Download Button
        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        st.download_button("💾 Template herunterladen", buf.getvalue(), "template.png", mime="image/png")

        # --- Weiterverarbeitung hier anschließen
        st.success("✅ Ausschnitt erstellt. Bereit für Weiterverarbeitung.")
    else:
        st.info("ℹ️ Bitte ziehe ein Rechteck auf dem Plan.")
else:
    st.info("⬆️ Lade eine PDF-Datei hoch, um zu starten.")









