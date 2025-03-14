# Use official Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy the files
COPY requirements.txt .
COPY app/ app/


# Install dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 8004

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
