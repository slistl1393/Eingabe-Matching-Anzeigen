# Start from a Python base image
FROM python:3.11-slim

# Install necessary system dependencies, including Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt to the container
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY backend /app

# Run the app using Uvicorn
CMD ["uvicorn", "grundfunktion:app", "--host", "0.0.0.0", "--port", "10000"]
