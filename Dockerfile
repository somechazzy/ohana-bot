# --- Builder stage ---
FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    libxml2-dev libxslt-dev \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/* \

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime stage ---
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libxml2 libxslt1.1 \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
CMD ["python", "main.py"]
