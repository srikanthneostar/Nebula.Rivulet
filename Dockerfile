FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    unixodbc \
    unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install the fabric wheel first
COPY fabric/dist/nebula_fabric-3.10.0-py3-none-any.whl /tmp/
RUN pip install --no-cache-dir /tmp/nebula_fabric-3.10.0-py3-none-any.whl && rm /tmp/nebula_fabric-3.10.0-py3-none-any.whl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy database
RUN mkdir -p /usr/Nebula.Rivulet/db
COPY commons/Nebula.Rivulet.db /usr/Nebula.Rivulet/db/

# Copy application code
COPY vertex/src /app/vertex/src
COPY rivulet/src /app/rivulet/src

# Set environment variables
ENV PYTHONPATH=/app
ENV NEBULA_RIVULET_HOME=/usr/Nebula.Rivulet/db

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "vertex.src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
