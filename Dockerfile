FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get clean

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip

RUN ls -la requirements.txt
RUN cat requirements.txt | head -10

RUN pip install --no-cache-dir -r requirements.txt

RUN pip list | grep fastapi

COPY . .

ENV PYTHONPATH=/app


CMD ["granian", "--interface", "asgi", "dialog_api.server:app", "--host", "0.0.0.0", "--port", "8002"]