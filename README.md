# Rushabh Kalme — Personal Portfolio

Static portfolio site for [rushabh.dev](https://rushabh.dev). Built with **Astro 5 + MDX + Tailwind CSS**, deployed on **Vercel**.

## Design

Cream paper surface (`#F5EFE6`) with vibrant orange-red accents (`#E55934` for fills, `#C8451F` for AA-safe text). Editorial typography pairing: **Fraunces** (variable 400/600/800) for the giant `RUSHABH` wordmark and section headings, **Instrument Serif italic** for accents like `I'm` and testimonial quotes, **Inter** for body, **JetBrains Mono** for code and eyebrows.

Every project card has a **topographic landscape cover** generated through the `mmx-cli` skill. All UI screenshots live under `public/images/projects/screens/<slug>-N.webp` and are used on the case-study pages.

## Editing content

- **Projects** — `src/content/projects/*.mdx`. Add a new file with full frontmatter; it will appear in the Projects section automatically.
  - `thumbnail` should point at the mmx-generated `/images/projects/cover-<slug>.webp`.
  - `images` array lists existing UI screenshots under `/images/projects/screens/`.
- **Experience** — `src/content/experience/*.mdx`. Numbered for sort order.
- **Patents & Publications** — `src/content/patents/*.yaml` (YAML data collection).
- **Achievements** — `src/content/achievements/*.yaml`.
- **Writing** — `src/content/writing/*.mdx`. Posts with `draft: true` are excluded from production.
- **Resume PDF** — replace `public/resume.pdf`.
- **Skills / Writing teasers / Testimonials** — content is currently hard-coded inline in `src/pages/index.astro` so you don't need to spin up MDX to edit them.
- **Polaroid portrait** — drop your photo at `public/images/rushabh-polaroid.jpg`; it appears in the hero automatically. Without the file, a monogram fallback renders.
- **og-image** — `public/og-image.svg` is the cream-themed SVG. Update the SVG directly to refresh social previews.

## Generating / regenerating project covers

The nine topographic covers ship pre-generated and committed under `public/images/projects/cover-<slug>.webp`. To regenerate one (after adjusting a prompt, for example):

```bash
mmx image generate \
  --prompt "Abstract topographic landscape illustrated in mid-century atlas style. Cream paper background (#F5EFE6). Fine navy contour lines (#1B2233) trace a <SUBJECT>. Sparse orange-red (#E55934) ridges mark high ground; sage green (#9CB69C) fills the valley basins. No text, no people, no UI, no logos. Sparse and editorial, soft paper grain." \
  --aspect-ratio 16:9 \
  --out-dir public/images/projects \
  --out-prefix cover-<slug> \
  --non-interactive --quiet
```

The `<SUBJECT>` and `<slug>` pairs are documented in `scripts/generate-assets.sh` (subject per project).

## Local development

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # static build (also runs astro check)
npm run preview  # serve the production build locally
```

## Layout

The home page is a single asymmetric flow:

- Hero (italic `I'm` + giant bold `RUSHABH` + Polaroid portrait + typewriter + metric strip).
- Two-column grid (desktop ≥ `lg`):
  - **Left**: featured cases (top two by sortOrder among `featured: true`) · experience · projects filter + remaining cards.
  - **Right (sticky)**: capabilities, journal (writing teasers), milestone timeline, testimonials, contact card.
- Patents & Publications spans full width.
- Bottom contact anchor + footer.

Mobile (`<lg`) collapses to a single-column scroll: hero, featured cases, experience, projects, then right-column items in Skills → Writing → Achievements → Testimonials → Contact order.

## Stack

- [Astro](https://astro.build) — static site generator
- [MDX](https://mdxjs.com) — content authoring
- [Tailwind CSS](https://tailwindcss.com) — styling (v3.4 with custom cream/orange theme)
- [Vercel Adapter](https://docs.astro.build/en/guides/integrations-guide/vercel/) — deployment
- [@vercel/analytics](https://vercel.com/analytics) — page-view tracking
- Inter + JetBrains Mono via [@fontsource](https://fontsource.org); Fraunces + Instrument Serif via Google Fonts (loaded through `media="print" onload="this.media='all'"` to keep render-blocking at zero)

## Deployment

Push to `main` → Vercel builds and deploys. `rushabh.dev` is attached in Vercel project settings.
