# Verwende das Python 3.11 Base Image
FROM python:3.11-slim

# Installiere Tesseract und andere Abhängigkeiten
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Erstelle und setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere die requirements.txt und installiere Python-Abhängigkeiten
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Codes
COPY . /app/

# Setze den Startbefehl
CMD ["uvicorn", "backend.grundfunktion:app", "--host", "0.0.0.0", "--port", "10000"]
