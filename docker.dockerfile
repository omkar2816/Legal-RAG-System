FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p uploads processed logs

# Copy application code
COPY . .

# Create .env file from template if it doesn't exist
RUN if [ ! -f .env ]; then cp env_template.txt .env; fi

# Expose the API port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app

# Command to run the application
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]