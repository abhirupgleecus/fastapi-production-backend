#Base image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

#Env variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

#Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

#Copy requirements file
COPY requirements.txt .

#Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Copy project files
COPY . .

#Expose port
EXPOSE 8000

#Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]