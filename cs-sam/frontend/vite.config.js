import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import legacy from '@vitejs/plugin-legacy'
import vue2 from '@vitejs/plugin-vue2'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue2(),
    legacy({
      targets: ['ie >= 11'],
      additionalLegacyPolyfills: ['regenerator-runtime/runtime']
    }),
    // plugin-legacy v2 hard-codes the modern chunk target to include safari11.1,
    // which lacks async generators (used by axios >= 1.7), so esbuild can't
    // transpile them. Re-set the target after it, bumping Safari to 12.
    // Older browsers still get the Babel-transpiled legacy chunk.
    {
      name: 'modern-target-override',
      enforce: 'post',
      config(config) {
        config.build = config.build || {}
        config.build.target = ['es2020', 'edge79', 'firefox67', 'chrome64', 'safari12']
      }
    }
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
