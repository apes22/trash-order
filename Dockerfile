# Multi-runtime: Node 22 + Python 3.11
FROM node:22-slim

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /app

# Install Node dependencies
COPY package.json package-lock.json ./
RUN npm ci --production

# Install Prisma and generate client
COPY prisma/ ./prisma/
RUN npx prisma generate

# Install Python dependencies
COPY requirements.txt ./
RUN python -m pip install --break-system-packages -r requirements.txt

# Copy all source files
COPY . .

# Expose port
EXPOSE ${PORT:-3000}

# Start both servers
CMD ["bash", "start.sh"]
