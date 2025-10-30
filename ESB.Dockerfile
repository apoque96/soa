FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create __init__.py files if they don't exist
RUN touch esb_core/__init__.py

EXPOSE 8001 8002 8003 8004

# Default command (can be overridden by docker-compose per-service)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]