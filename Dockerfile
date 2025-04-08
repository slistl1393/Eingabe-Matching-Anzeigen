FROM python:3.10-slim

# System-Dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean

# Arbeitsverzeichnis setzen
WORKDIR /app

# Dateien kopieren
COPY . /app

# Python-Abhängigkeiten installieren
RUN pip install --no-cache-dir -r backend/requirements.txt

# Startkommando
CMD ["uvicorn", "backend.grundfunktion:app", "--host", "0.0.0.0", "--port", "10000"]
