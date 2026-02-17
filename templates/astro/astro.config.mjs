import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  // Uncomment and set your site URL for sitemap generation and canonical URLs
  // site: 'https://example.com',
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
