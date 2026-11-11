FROM node:18-alpine

WORKDIR /app

# Skip Cypress binary download (E2E-only devDependency, not needed to build)
ENV CYPRESS_INSTALL_BINARY=0

# NEXT_PUBLIC_* variables are inlined into the client bundle at build time.
# For the single-domain Coolify deployment (docker-compose.coolify.yml) this is
# set to the SAME-ORIGIN relative path "/api/v1": the browser calls the frontend
# domain and Next.js proxies /api/* to the backend (see API_PROXY_TARGET below).
# For local dev builds outside compose, keep the direct backend URL.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build-time target for the /api/* reverse proxy defined in next.config.js.
# Rewrites are resolved at build time, so this must be an ARG (not runtime env).
# Default matches the `backend` service name in docker-compose.coolify.yml.
ARG API_PROXY_TARGET=http://backend:8000
ENV API_PROXY_TARGET=$API_PROXY_TARGET

# Install dependencies from the lockfile (devDependencies required for the build)
COPY frontend-qa/package.json frontend-qa/package-lock.json ./
RUN npm ci

# Copy source and produce the production build
COPY frontend-qa ./
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
