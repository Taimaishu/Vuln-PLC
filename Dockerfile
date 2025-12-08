FROM python:3.9-slim

LABEL maintainer="Security Training"
LABEL description="Vulnerable PLC Simulator for ICS/SCADA Security Testing"

# Install system dependencies for packet capture and networking tools
RUN apt-get update && apt-get install -y \
    gcc \
    libpcap-dev \
    tcpdump \
    net-tools \
    iputils-ping \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY core/ core/
COPY monitoring/ monitoring/
COPY scripts/ scripts/
COPY templates/ templates/
COPY docs/ docs/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/pcaps /tmp

# Expose ports for all services
# PLC web interfaces: 5000-5013
# Modbus TCP: 5502-5505
# Historian: 8888
# System Monitor: 5999
# S7 Protocol: 102
EXPOSE 5000 5011 5012 5013 5502 5503 5504 5505 8888 5999 102

# Default command (can be overridden in docker-compose)
CMD ["python", "start.py"]
