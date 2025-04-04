import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import io
import requests
import json
import pandas as pd
import plotly.express as px
from streamlit_drawable_canvas import st_canvas

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
uploaded_pdf = st.file_uploader("🔼 Lade deinen Plan als PDF hoch", type=["pdf"])

if uploaded_pdf:
    st.subheader("⚙️ Einstellungen")
    dpi = st.slider("Wähle die DPI für die PDF-Konvertierung", min_value=100, max_value=400, value=300, step=50)

    # --- PDF -> Image ---
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    num_pages = len(doc)
    page_num = st.number_input("Seitenzahl wählen", min_value=1, max_value=num_pages, value=1)
    image_pil = convert_pdf_page_to_image(doc.write(), dpi=dpi, page_number=page_num - 1).convert("RGB")

    # In-Memory PNG erzeugen
    image_bytes = io.BytesIO()
    image_pil.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    st_image_for_canvas = Image.open(image_bytes)
    st_image_for_canvas.format = 'PNG'


    st.subheader(f"🖼️ Vorschau – Seite {page_num} (DPI: {dpi})")
    st.image(image_pil, use_column_width=True)

    # --- Template Auswahl per Ziehen eines Kästchens ---
    st.subheader("✂️ Ziehe ein Rechteck über den gewünschten Template-Bereich")
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=3,
        background_image=st_image_for_canvas,
        update_streamlit=True,
        height=st_image_for_canvas.height,
        width=st_image_for_canvas.width,
        drawing_mode="rect",
        key="canvas",
    )

    if canvas_result.json_data and canvas_result.json_data["objects"]:
        obj = canvas_result.json_data["objects"][0]
        left = int(obj["left"])
        top = int(obj["top"])
        width = int(obj["width"])
        height = int(obj["height"])

        # --- Ausschnitt extrahieren ---
        cropped = image_pil.crop((left, top, left + width, top + height))
        st.subheader("📦 Ausgeschnittenes Template")
        st.image(cropped, caption="Dein Template-Ausschnitt", use_column_width=False)

        # --- Option zum Speichern / Weitergeben ---
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
        st.info("🧠 Nächster Schritt: Template Matching und Auswertung (hier simuliert)")

        # --------------------------------------------------
        # --- 🔍 SIMULIERTER ANALYSE- UND ANZEIGETEIL ----
        # --------------------------------------------------

        st.header("📦 Übersicht erkannter Bauteile")

        # Beispielhafter Platzhalter-JSON (würde aus Colab kommen)
        sample_json = [{
            "bauteil": "Isokorb XT",
            "count": 4,
            "matches": [
                {"position": {"x": 150, "y": 200}, "template": "template.png", "bauteil": "Isokorb XT"},
                {"position": {"x": 420, "y": 180}, "template": "template.png", "bauteil": "Isokorb XT"},
                {"position": {"x": 610, "y": 380}, "template": "template.png", "bauteil": "Isokorb XT"},
                {"position": {"x": 250, "y": 480}, "template": "template.png", "bauteil": "Isokorb XT"}
            ]
        }]

        for template in sample_json:
            bauteil = template.get("bauteil", "Unbekannt")
            count = template.get("count", len(template.get("matches", [])))

            with st.expander(f"{bauteil} ({count}x erkannt)"):
                st.write("**🔹 Info:** Beispielhafte Analyse")
                st.markdown("---")
                st.subheader("📍 Trefferpositionen:")
                st.json(template.get("matches", []))

        # --- Visualisierung der Treffer ---
        st.header("🗺️ Treffer auf Gesamtplan")
        df = pd.DataFrame([
            {"x": m["position"]["x"], "y": m["position"]["y"], "bauteil": m.get("bauteil", "Unbekannt")}
            for t in sample_json for m in t.get("matches", [])
        ])

        fig = px.imshow(image_pil, binary_format="jpg")
        fig.update_layout(title="📍 Treffer auf dem Gesamtplan", width=1200, height=800)
        fig.add_scatter(
            x=df["x"], y=df["y"], mode="markers", marker=dict(size=10, color="red"),
            text=df["bauteil"], name="Treffer"
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("⬆️ Bitte lade zunächst eine PDF-Datei hoch.")


