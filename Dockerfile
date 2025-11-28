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

# Copy all wheel files
COPY fabric/dist/nebula_fabric-3.10.0-py3-none-any.whl /tmp/
COPY rivulet/dist/nebula_rivulet-3.10.0-py3-none-any.whl /tmp/
COPY vertex/dist/nebula_vertex-3.10.0-py3-none-any.whl /tmp/

# Install wheels in waterfall order: fabric -> rivulet -> vertex
RUN pip install --no-cache-dir /tmp/nebula_fabric-3.10.0-py3-none-any.whl && \
    pip install --no-cache-dir /tmp/nebula_rivulet-3.10.0-py3-none-any.whl && \
    pip install --no-cache-dir /tmp/nebula_vertex-3.10.0-py3-none-any.whl && \
    rm /tmp/*.whl

# Install requirements 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source files to /app (main.py, auth.py, app.py, etc.)
COPY vertex/src/ /app/

# Copy database
RUN mkdir -p /usr/Nebula.Rivulet/db
COPY commons/Nebula.Rivulet.db /usr/Nebula.Rivulet/db/
COPY commons/knowledge_db /usr/Nebula.Rivulet/db/knowledge_db

# Set environment variables
ENV NEBULA_RIVULET_HOME=/usr/Nebula.Rivulet/db
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--ssl-keyfile", "key.pem", "--ssl-certfile", "cert.pem"]
