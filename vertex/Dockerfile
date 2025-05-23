FROM python:3.12-slim

RUN mkdir -p /usr/Nebula.Rivulet
RUN mkdir -p /usr/Nebula.Rivulet/db
COPY /Nebula.Rivulet.db /usr/Nebula.Rivulet/db
ENV NEBULA_RIVULET_HOME=/usr/Nebula.Rivulet/db

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
RUN pip install /usr/Nebula.Rivulet/fabric/dist/nebula_fabric-3.10.0-py3-none-any.whl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY vertex/src /app/vertex/src

# Set environment variables
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8000

# Create a script to run both the FastAPI app and Celery worker
# celery -A app worker --concurrency=4 --pool=threads  --loglevel=INFO --logfile=celery_debug.log --events
RUN echo '#!/bin/bash\n\
celery -A vertex.src.api.app worker --loglevel=info &\n\
uvicorn vertex.src.api.main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Command to run the application
CMD ["/app/start.sh"]
