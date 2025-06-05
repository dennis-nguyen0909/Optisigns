# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Run the daily worker with schedule
CMD ["python", "daily_job.py"]

# docker build -t optisign-bot .
# docker run -it --env-file .env optisign-bot
# docker run -e OPEN_API_KEY=sk- optisignbot