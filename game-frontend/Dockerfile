# Step 1: Use an official Node.js image as base
FROM node:18-alpine

# Step 2: Set working directory inside the container
WORKDIR /app

# Step 3: Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Step 4: Copy the rest of your project files
COPY . .

# Step 5: Expose the port React uses by default
EXPOSE 3000

# Step 6: Start the React development server
CMD ["npm", "start"]
