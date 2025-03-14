# Use an official Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy requirements file first (for efficient caching)
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the application code AFTER installing dependencies
COPY app/ app/

# Expose port
EXPOSE 8001

# Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
