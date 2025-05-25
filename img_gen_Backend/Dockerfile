# Use a Python base image
FROM python:3.9-slim

# Install OpenJDK 11 (via default-jdk) and other necessary packages
RUN apt-get update && apt-get install -y \
    default-jdk \
    python3-pip \
    && apt-get clean

# Set environment variables for Java (path might vary; check with 'update-alternatives --config java')
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Set up working directory in the container
WORKDIR /app

# Copy requirements file to the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . /app/

# Expose the Flask application port
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]