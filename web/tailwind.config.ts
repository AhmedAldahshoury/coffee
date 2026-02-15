import type { Config } from 'tailwindcss';

export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#f5f1eb',
        foreground: '#2b2118',
        card: '#fffdf9',
        border: '#e8dfd4',
        primary: '#5b3a29',
      },
    },
  },
  plugins: [],
} satisfies Config;
