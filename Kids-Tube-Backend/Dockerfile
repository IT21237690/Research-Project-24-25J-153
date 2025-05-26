# Use an official Node.js LTS image
FROM node:18

# Create and set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app files
COPY . .

# Expose the port app runs on
EXPOSE 7000

# Start the app
CMD ["node", "server-fixed.js"]
