FROM python:3.11-slim

# Install Node 22
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy package.json and install Node dependencies
COPY package.json ./
RUN npm install --no-package-lock

# Copy Prisma schema and generate client
COPY prisma/ ./prisma/
RUN npx prisma generate

# Copy all source files
COPY . .

RUN chmod +x start.sh

EXPOSE 3000

CMD ["bash", "start.sh"]
