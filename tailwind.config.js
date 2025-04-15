/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        background: '#121212',
        'surface-dark': '#1E1E1E',
        'surface-light': '#2E2E2E',
        'text-primary': '#FFFFFF',
        'text-secondary': '#B3B3B3',
        accent: '#E50914',
      },
      height: {
        '35vh': '35vh',
      },
      minHeight: {
        'carousel': '200px',
      }
    },
  },
  plugins: [],
} 