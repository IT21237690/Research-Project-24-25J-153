# Use the official Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all project files to the working directory
COPY . .

# Install required system packages and Python libraries
RUN pip install --no-cache-dir flask pandas numpy scikit-learn joblib

# Expose the port Flask runs on
EXPOSE 5001

# Run the Flask application
CMD ["python", "app.py"]
