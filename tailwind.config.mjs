/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          50:  'var(--cream-50)',
          100: 'var(--cream-100)',
          200: 'var(--cream-200)',
          300: 'var(--cream-300)',
        },
        ink: {
          900: 'var(--ink-900)',
          700: 'var(--ink-700)',
          500: 'var(--ink-500)',
          300: 'var(--ink-300)',
        },
        accent: {
          600: 'var(--orange-600)',
          500: 'var(--orange-500)',
          300: 'var(--orange-300)',
          DEFAULT: 'var(--orange-500)',
        },
        sage: {
          600: 'var(--sage-600)',
          400: 'var(--sage-400)',
        },
        sky:   { 700: 'var(--sky-700)' },
        line:  'var(--line)',
      },
      fontFamily: {
        sans:    ['"Inter Variable"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono:    ['"JetBrains Mono Variable"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
        serif:   ['"Instrument Serif"', '"Fraunces"', 'ui-serif', 'Georgia', 'serif'],
        display: ['"Fraunces"', '"Instrument Serif"', 'ui-serif', 'Georgia', 'serif'],
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
