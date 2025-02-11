FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY pipeline/extract.py .
COPY pipeline/transform.py .
COPY pipeline/load.py .
COPY pipeline/etl.py .

CMD ["python", "etl.py"]