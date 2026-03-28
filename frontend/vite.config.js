import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'node:path'
import os from 'node:os'

// https://vite.dev/config/
export default defineConfig({
  // Vite/esbuild must write pre-bundled deps here. Using the system temp dir avoids
  // "operation not permitted" when the repo or node_modules tree is not writable
  // (sandboxed IDEs, hardened node_modules, macOS privacy tools, etc.).
  cacheDir: path.join(os.tmpdir(), 'mirofish-en-vite-cache'),
  plugins: [vue()],
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
