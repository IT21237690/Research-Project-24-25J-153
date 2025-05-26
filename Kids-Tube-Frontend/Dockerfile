# Use official Node.js LTS image
FROM node:18

# Set working directory
WORKDIR /app

# Copy package.json and lock file
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app
COPY . .

# Expose the port used by npm start (3000 by default, or 3001 if set in your package.json)
EXPOSE 3000

# Start the React app in development mode
CMD ["npm", "start"]
