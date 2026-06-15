import { defineConfig } from 'vitest/config'
import path from 'path'

export default defineConfig({
  resolve: {
    alias: {
      react: path.resolve(__dirname, 'node_modules/react'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom')
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['**/*.test.{js,jsx}'],
    setupFiles: ['./setupTests.js']
  }
})
