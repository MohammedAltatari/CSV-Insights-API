# Base image: official slim Python runtime
FROM python:3.13-slim

# Python runtime settings: no .pyc files, unbuffered logs, no pip cache
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Working directory inside the container
WORKDIR /app

# Install dependencies first to benefit from Docker layer caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy only the application source code
COPY src/ ./src/

# Run as a non-root user for better security
RUN useradd --create-home appuser
USER appuser

# The API listens on port 8000
EXPOSE 8000

# Report container health by calling the /health endpoint every 30 seconds
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

# Start the API server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
