/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        mist: "#eef3f7",
        teal: "#117c78",
        amber: "#c47a18",
        rose: "#b9384f"
      }
    }
  },
  plugins: []
};
