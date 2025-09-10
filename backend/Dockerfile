FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ .
COPY backend/.ipython /root/.ipython/
COPY backend/.jupyter /root/.jupyter/

# Expose Flask port
EXPOSE 8080

# Set environment variables for Flask
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV ENABLE_TIMESCALE_INIT=true

CMD ["flask", "run", "--reload"]
