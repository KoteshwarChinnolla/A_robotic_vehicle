FROM python:3.12.4-alpine3.20

# We need curl for the health check
RUN apk --no-cache add curl

WORKDIR /app

# First, copy dependencies only
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copying the app source separately significantly improves 
# build time by using the cache if no new dependencies are added
COPY app.py .
COPY agent/ ./agent
COPY astar.py .
COPY image_toMatrix.py .
COPY lastpossition.json .
COPY images/ ./images

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
# CMD ["uvicorn", "--host", "0.0.0.0:8080", "app:app"]