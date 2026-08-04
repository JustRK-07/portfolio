# Rushabh Kalme — Personal Portfolio

Static portfolio site for [rushabh.dev](https://rushabh.dev). Built with **Astro 5 + MDX + Tailwind CSS**, deployed on **Vercel**.

## Local development

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # static build to dist/
npm run preview  # serve the production build locally
```

## Editing content

- **Projects** — `src/content/projects/*.mdx`. Add a new file with full frontmatter; it will appear in the Projects section automatically.
- **Experience** — `src/content/experience/*.mdx`. Numbered for sort order.
- **Patents & Publications** — `src/content/patents/patents.yaml` (YAML data collection).
- **Achievements** — `src/content/achievements/achievements.yaml`.
- **Writing** — `src/content/writing/*.mdx`. Posts with `draft: true` are excluded from production.
- **Resume PDF** — replace `public/resume.pdf`.

## Design

- Dark navy base (`#07111f`) with teal accent (`#2dd4bf`)
- Sticky left sidebar (desktop ≥1024px) / top bar (mobile/tablet)
- One signature interaction: a typewriter terminal in the hero
- No chatbot, no glassmorphism — engineer-console aesthetic

## Stack

- [Astro](https://astro.build) — static site generator
- [MDX](https://mdxjs.com) — content authoring
- [Tailwind CSS](https://tailwindcss.com) — styling
- [Vercel Adapter](https://docs.astro.build/en/guides/integrations-guide/vercel/) — deployment
- Inter + JetBrains Mono via [Fontsource](https://fontsource.org)

## Deployment

Push to `main` → Vercel builds and deploys. The custom domain `rushabh.dev` is attached in Vercel project settings.
