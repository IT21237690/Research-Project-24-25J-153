# Use an official Node.js runtime as a base image
FROM node:18

# Set working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Expose port 5000 (or your API port)
EXPOSE 5000

# Start the server
CMD ["npm", "run", "dev"]
