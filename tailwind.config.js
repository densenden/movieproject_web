module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        background: '#141414',
        surface: '#222',
        'surface-dark': '#000',
        'text-primary': '#ffffff',
        'text-secondary': '#aaaaaa',
        accent: '#e50914',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        heading: ['Bebas', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
    }
  },
  plugins: [],
} 