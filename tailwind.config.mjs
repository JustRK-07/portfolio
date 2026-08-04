/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: 'var(--navy-950)',
          900: 'var(--navy-900)',
          850: 'var(--navy-850)',
        },
        slate: {
          700: 'var(--slate-700)',
          500: 'var(--slate-500)',
          300: 'var(--slate-300)',
        },
        ink: 'var(--text-primary)',
        teal: {
          DEFAULT: 'var(--teal-500)',
          400: 'var(--teal-400)',
          deep: 'var(--teal-deep)',
        },
        line: 'var(--line)',
        surface: 'var(--surface-hover)',
      },
      fontFamily: {
        sans: ['"Inter Variable"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono Variable"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
        display: ['"IBM Plex Serif"', 'ui-serif', 'Georgia', 'serif'],
      },
      letterSpacing: {
        'meta': '0.12em',
      },
      maxWidth: {
        'content': '1280px',
        'prose-thin': '60ch',
      },
    },
  },
  plugins: [],
};
