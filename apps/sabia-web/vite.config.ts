import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  optimizeDeps: {
    exclude: ['bits-ui', 'mode-watcher', 'svelte-sonner', 'layercake', '@lucide/svelte'],
  },
  ssr: {
    noExternal: ['bits-ui', 'mode-watcher', 'svelte-sonner'],
    external: ['layercake'],
  },
  server: {
    fs: { allow: ['..'] },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
