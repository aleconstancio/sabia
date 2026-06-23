import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const config = {
  preprocess: vitePreprocess(),
  compilerOptions: {
    runes: ({ filename }) => filename && !filename.includes('node_modules') ? true : undefined
  },
  kit: {
    adapter: adapter({
      fallback: 'index.html',
    }),
  },
};
export default config;
