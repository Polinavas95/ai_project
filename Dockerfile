FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get clean

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip

RUN ls -la requirements.txt
RUN cat requirements.txt | head -10

RUN pip install --no-cache-dir \
    fastapi==0.121.3 \
    uvicorn==0.38.0 \
    granian==2.6.0 \
    gigachat==0.1.43 \
    pydantic==2.12.4 \
    python-dotenv==1.2.1 \
    aiohttp==3.13.2

RUN pip install --no-cache-dir -r requirements.txt

RUN pip list | grep fastapi
RUN python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"

COPY . .

RUN ls -la
RUN find . -name "*.py" | head -10

ENV PYTHONPATH=/app


CMD ["python", "-m", "dialog_api.server"]