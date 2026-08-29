/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0B1F33",
        marine: "#0F4C81",
        marineLight: "#3E7CB1",
        sand: "#F6F3EC",
        coral: "#E4572E",
        moss: "#2E7D5B",
        slate: "#5B6B79",
      },
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        body: ["'Inter'", "sans-serif"],
      },
      borderRadius: {
        xl2: "1.25rem",
      },
    },
  },
  plugins: [],
};
