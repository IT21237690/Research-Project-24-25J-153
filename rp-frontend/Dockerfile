# Step 1: Use Node.js image to build the app
FROM node:18 AS build

WORKDIR /app

# Copy package.json and package-lock.json to install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the app's files
COPY . .

# Build the React app
RUN npm run build

# Step 2: Use Nginx to serve the built app
FROM nginx:alpine

# Copy the build output from the build stage to the Nginx html directory
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

# Start Nginx to serve the app
CMD ["nginx", "-g", "daemon off;"]
