import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'https://example.com',
  outDir: './dist',
  publicDir: './public',
  build: {
    assets: '_astro'
  },
  vite: {
    build: {
      cssCodeSplit: false
    }
  }
});
