import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import vercel from '@astrojs/vercel';

// https://astro.build/config
export default defineConfig({
  site: 'https://rushabh-kalme.vercel.app',
  output: 'static',
  integrations: [
    mdx(),
    tailwind({ applyBaseStyles: false }),
    sitemap(),
  ],
  adapter: vercel(),
  build: {
    inlineStylesheets: 'auto',
  },
  // The AGV project slug was corrected from "bekeart" to "bekaert" — keep the
  // old URL working rather than 404 it. Astro emits an exact-match Vercel
  // route here; vercel.json covers the trailing-slash form too.
  redirects: {
    '/projects/10-bekeart-agv': '/projects/10-bekaert-agv',
  },
});
