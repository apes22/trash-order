# Multi-runtime: Node 22 + Python 3.11
FROM node:22-slim

# Install Python + bash
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv bash && \
    rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /app

# Install Node dependencies (including devDependencies for prisma CLI)
COPY package.json ./
RUN npm install --no-package-lock

# Install Prisma and generate client
COPY prisma/ ./prisma/
RUN npx prisma generate

# Install Python dependencies
COPY requirements.txt ./
RUN python -m pip install --break-system-packages --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Make start script executable
RUN chmod +x start.sh

EXPOSE 3000

CMD ["bash", "start.sh"]
