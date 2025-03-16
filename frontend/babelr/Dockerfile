# Use Node.js
FROM node:22.14.0 AS builder

# Set the working directory
WORKDIR /usr/src/app

# Copy package files 
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install --production

# Copy the entire project (including /pages/)
COPY . .

# Build the Next.js application
RUN npm run build

# Use a smaller image for running the app
FROM node:22.14.0-alpine AS runner
WORKDIR /usr/src/app

# Set environment to production
ENV NODE_ENV=production

# Copy only necessary files from the builder
COPY --from=builder /usr/src/app/.next ./.next
COPY --from=builder /usr/src/app/public ./public
COPY --from=builder /usr/src/app/package.json ./
COPY --from=builder /usr/src/app/node_modules ./node_modules
COPY --from=builder /usr/src/app/pages ./pages
COPY --from=builder /usr/src/app/components ./components
COPY --from=builder /usr/src/app/stylesheets ./stylesheets

# Expose the Next.js server port
EXPOSE 3000

# Start the Next.js app
CMD ["npm", "run", "start"]