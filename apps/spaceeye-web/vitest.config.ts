import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

export default defineConfig({
  plugins: [svelte()],
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['src/__tests__/**/*.test.ts'],
    setupFiles: ['src/__tests__/setup.ts'],
  },
  resolve: {
    alias: {
      $lib: path.resolve('./src/lib'),
      '$app/stores': path.resolve('./src/__mocks__/app/stores.ts'),
      '$app/navigation': path.resolve('./src/__mocks__/app/navigation.ts'),
      '$app/environment': path.resolve('./src/__mocks__/app/environment.ts'),
    },
  },
});
