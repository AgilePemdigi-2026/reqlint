FROM node:18-alpine

WORKDIR /app

# Skip Cypress binary download (E2E-only devDependency, not needed to build)
ENV CYPRESS_INSTALL_BINARY=0

# NEXT_PUBLIC_* variables are inlined into the client bundle at build time.
# In Coolify, set this build arg to the public backend URL, e.g.
# https://<backend-domain>/api/v1
ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Install dependencies from the lockfile (devDependencies required for the build)
COPY frontend-qa/package.json frontend-qa/package-lock.json ./
RUN npm ci

# Copy source and produce the production build
COPY frontend-qa ./
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
