# ---------- Stage 1: builder - install the dependencies ----------
FROM python:3.13-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install packages into a separate folder that the final stage will copy,
# then remove the test suites bundled inside packages (e.g. pandas, numpy): not needed at runtime
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt \
    && find /install -type d -name tests -prune -exec rm -rf {} +

# ---------- Stage 2: runtime - only what the API needs to run ----------
FROM python:3.13-slim

# Python runtime settings: no .pyc files and unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Working directory inside the container
WORKDIR /app

# Copy the installed packages from the builder stage
COPY --from=builder /install /usr/local

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
