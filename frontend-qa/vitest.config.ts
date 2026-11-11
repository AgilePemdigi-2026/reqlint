import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  resolve: {
    // Samakan alias '@' dengan tsconfig paths Next.js agar modul yang
    // memakai '@/' bisa diuji langsung oleh vitest.
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    // Unit tests of the analyzer/lib only. Cypress E2E specs (tests-e2e/**)
    // are NOT vitest tests — they run through `cypress` (FUNC-19 tracks their
    // staleness separately).
    include: ['src/**/*.test.ts'],
    environment: 'node',
  },
});
