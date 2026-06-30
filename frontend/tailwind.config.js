/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        clinical: { 950: '#06091a', 900: '#0a0f1e', 800: '#0d1526', 700: '#112240' },
        teal:     { 300: '#5eead4', 400: '#2dd4bf', 500: '#14b8a6' },
        risk:     { low: '#22c55e', medium: '#f59e0b', high: '#ef4444' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
