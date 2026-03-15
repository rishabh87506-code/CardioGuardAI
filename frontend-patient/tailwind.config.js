/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    dark: '#0f172a',
                    primary: '#3b82f6',
                    accent: '#ef4444', // Red for alert
                    success: '#10b981'
                }
            }
        },
    },
    plugins: [],
}
