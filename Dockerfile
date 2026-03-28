# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy entire project

COPY . .
# Expose port (Flask default)

EXPOSE 5000
# Environment variables

ENV PYTHONUNBUFFERED=1

# Run the app
CMD ["python", "application.py"]
