import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Configuración de Vite. El plugin de React permite usar JSX.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // Dirección local: http://localhost:5173
    // Solo en desarrollo: las peticiones que empiezan con /api se reenvían a Django.
    // Así React llama a "/api/health/" y Vite lo entrega a http://127.0.0.1:8000
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});
