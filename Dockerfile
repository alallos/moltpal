FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run migrations on startup, then start server
CMD ["sh", "-c", "npm run db:migrate && npm start"]
