# Start von einem Python 3.11-Image
FROM python:3.11

# Arbeitsverzeichnis festlegen
WORKDIR /app

# Anforderungen installieren
COPY requirements.txt .
RUN pip install -r requirements.txt

# Tesseract installieren
RUN apt-get update && apt-get install -y tesseract-ocr

# Arbeitsverzeichnis ins Container verlagern
COPY ./backend /app/backend

# Exponiere den Port
EXPOSE 10000

# Starten der API mit uvicorn
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "10000"]


