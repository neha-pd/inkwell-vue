import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
export default defineConfig(({ mode }) => ({
 plugins: [vue()], base: './',
 build: mode === 'library' ? {
  lib: { entry: 'src/index.js', formats: ['es'], fileName: 'inkwell-vue', cssFileName: 'inkwell-vue' },
  rollupOptions: { external: id => id === 'vue' || id.startsWith('@tiptap/') || id === 'dompurify' }
 } : { outDir: 'docs' }
}))
