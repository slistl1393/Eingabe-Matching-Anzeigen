# Verwenden von Python als Basis-Image
FROM python:3.11-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die Anforderungen in den Container
COPY requirements.txt /app/

# Installiere systemweite Abhängigkeiten (wie tesseract)
RUN apt-get update && apt-get install -y tesseract-ocr

# Installiere Python-Abhängigkeiten
RUN pip install -r requirements.txt

# Kopiere den gesamten Code ins Arbeitsverzeichnis
COPY . /app/

# Stelle sicher, dass der Pfad für tesseract korrekt ist
RUN ln -s /usr/bin/tesseract /usr/local/bin/tesseract

# Setze den Befehl, um die FastAPI-Anwendung zu starten
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "10000"]

