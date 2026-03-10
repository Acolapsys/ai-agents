// tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'charcoal-blue': '#2f4858',
        'baltic-blue': '#33658a',
        'sky-reflection': '#86bbd8',
        'honey-bronze': '#f6ae2d',
        'blaze-orange': '#f26419',
      },
    },
  },
  plugins: [],
}