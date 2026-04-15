FROM node:18-alpine

WORKDIR /app

# Copy package management files
COPY package.json package-lock.json ./
RUN npm install

# Copy application files
COPY . .

# The next js app listens on port 3000 by default, let's expose it
ENV PORT=3000
EXPOSE 3000

# Build the Next.js app
RUN npm run build

# Start the application
CMD ["npm", "start"]
