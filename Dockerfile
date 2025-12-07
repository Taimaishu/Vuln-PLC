FROM python:3.9-slim

LABEL maintainer="Security Training"
LABEL description="Vulnerable PLC Simulator for Security Testing"

# Create app directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY modbus_server.py .
COPY start.py .
COPY templates/ templates/

# Create database directory
RUN mkdir -p /app/data

# Expose ports
EXPOSE 5000 5502

# Run startup script
CMD ["python", "start.py"]
