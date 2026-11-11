/**
 * Reverse-proxy target for /api/* requests, used by the single-domain
 * Coolify deployment (docker-compose.coolify.yml). Next.js resolves the
 * destination server-side, so the Docker-internal service name works even
 * though browsers can never resolve it.
 *
 * NOTE: rewrites are resolved at BUILD time (baked into routes-manifest.json),
 * so this must be provided as a Docker build arg, not a runtime env var.
 * The default matches the `backend` service name in docker-compose.coolify.yml.
 * Locally this env stays unset and the rewrites stay dormant: the dev server
 * calls the backend directly via NEXT_PUBLIC_API_URL (see .env.example).
 */
const API_PROXY_TARGET = process.env.API_PROXY_TARGET || 'http://backend:8000';

/** @type {import('next').NextConfig} */
const nextConfig = {
  outputFileTracing: false,
  async rewrites() {
    return {
      // afterFiles: filesystem routes (frontend pages) always win first,
      // so these proxies can never shadow a frontend route.
      afterFiles: [
        {
          source: '/api/:path*',
          destination: `${API_PROXY_TARGET}/api/:path*`,
        },
        // Optional: expose FastAPI documentation through the same domain.
        // (Swagger UI itself fetches /api/v1/openapi.json, which the rule above covers.)
        {
          source: '/docs',
          destination: `${API_PROXY_TARGET}/docs`,
        },
        {
          source: '/redoc',
          destination: `${API_PROXY_TARGET}/redoc`,
        },
      ],
    };
  },
  async redirects() {
    return [
      {
        source: '/upload',
        destination: '/editor',
        permanent: false,
      },
      {
        source: '/signup',
        destination: '/register',
        permanent: false,
      },
      {
        source: '/audit',
        destination: '/editor',
        permanent: false,
      },
      {
        source: '/audit/hasilAudit',
        destination: '/history',
        permanent: false,
      },
    ];
  },
};

module.exports = nextConfig;
