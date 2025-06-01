FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libpng-dev \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    libtiff5-dev \
    libx11-dev \
    libxft-dev \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# RUN apk --no-cache add curl

RUN pip install --upgrade pip setuptools wheel

WORKDIR /app


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY agent/ ./agent
COPY astar.py .
COPY image_toMatrix.py .
COPY lastpossition.json .
COPY images/ ./images
COPY arduino_send.py .

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]