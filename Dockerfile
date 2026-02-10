FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output/temp output/videos output/scripts output/voiceovers output/thumbnails

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1", "app:app"]
