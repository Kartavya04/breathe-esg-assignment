# Use an official lightweight Python image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . /app/

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run migrations and start gunicorn
CMD ["sh", "-c", "python manage.py collectstatic --no-input && python manage.py migrate && gunicorn --bind :$PORT core.wsgi:application"]