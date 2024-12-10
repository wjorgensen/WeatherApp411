FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy .env file
COPY .env .

# Copy rest of the application
COPY . .

# Initialize the database
RUN flask init-db

# Expose port for the Flask app
EXPOSE 5000

# Start both the Flask app and the main program
CMD flask run --host=0.0.0.0 & python run.py
