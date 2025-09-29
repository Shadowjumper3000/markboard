# Multi-stage build for production frontend
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
COPY bun.lockb ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application for production
RUN npm run build

# Production stage - lightweight nginx for serving static files
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration for internal serving
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user for security
RUN addgroup -g 1001 -S nginx-user && \
    adduser -S nginx-user -u 1001 -G nginx-user

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]