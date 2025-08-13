# Use official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY app.py .

# Expose Flask port
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "app.py"]
