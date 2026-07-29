# Use Python 3.11 slim as the base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for compiling certain python packages like asyncpg, psycopg)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code and data files
COPY backend/ ./backend/
COPY data/ ./data/

# Copy the environment file
COPY .env .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the FastAPI server on port 8004 by default
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8004"]
