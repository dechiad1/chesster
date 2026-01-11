/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          dark: '#0f3460',
          DEFAULT: '#16213e',
          light: '#1a1a2e'
        },
        accent: {
          blue: '#4a9eff',
          green: '#28a745',
          red: '#dc3545'
        },
        surface: {
          dark: '#253156',
          DEFAULT: '#2a3a5a'
        },
        text: {
          primary: '#ffffff',
          secondary: '#b0b0b0',
          muted: '#888888'
        }
      },
    },
  },
  plugins: [],
}
