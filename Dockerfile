FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

EXPOSE 10000

CMD ["gunicorn", "backend.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:10000", "--timeout", "120"]
