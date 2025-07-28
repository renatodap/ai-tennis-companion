# Use Python 3.11 base image
FROM python:3.11-slim

# System dependencies for mediapipe + opencv
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose port
EXPOSE 10000

# Start FastAPI app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]
