import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import tailwind from '@astrojs/tailwind';
import vercel from '@astrojs/vercel';

// https://astro.build/config
export default defineConfig({
  site: 'https://rushabh.dev',
  output: 'static',
  integrations: [
    mdx(),
    tailwind({ applyBaseStyles: false }),
  ],
  adapter: vercel(),
  build: {
    inlineStylesheets: 'auto',
  },
});
