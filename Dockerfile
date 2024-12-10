FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY database.py .
COPY auth.py .
COPY run.py .
COPY schema.sql .

RUN pip install --no-cache-dir -r requirements.txt



EXPOSE 5000

CMD ["sh", "-c", "flask init-db && python app.py & python run.py"]
