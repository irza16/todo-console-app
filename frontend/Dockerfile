FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies (including dev dependencies needed for build)
RUN npm ci

# Copy source code
COPY . .

# Build the Next.js app
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

# Install dumb-init to handle PID 1 properly
RUN apk add --no-cache dumb-init

# Copy node modules from builder stage
COPY --from=builder /app/node_modules ./node_modules
# Copy built application from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./package.json

# Create non-root user
RUN addgroup -g 1001 -S nextjs && \
    adduser -S nextjs -u 1001

# Change ownership of the app directory to nextjs user
RUN chown -R nextjs:nextjs /app
USER nextjs

# Expose port
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Start the application with dumb-init
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]