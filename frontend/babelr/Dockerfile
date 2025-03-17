# Use Node.js for building
FROM node:22.14.0-alpine AS builder

# Set the working directory
WORKDIR /usr/src/app

# Copy package files (for efficient caching)
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install 

# Copy the full source code
COPY . .

# Build the Next.js application
RUN npm run build

# Expose the Next.js server port
EXPOSE 3000

# Start the Next.js app
CMD ["npm", "run", "start"]