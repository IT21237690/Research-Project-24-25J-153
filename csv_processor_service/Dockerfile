# Use official Python image (3.10)
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy the files
COPY requirements.txt .
COPY app/ app/


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
