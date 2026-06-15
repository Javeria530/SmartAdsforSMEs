import { vi } from 'vitest'
import React from 'react'

// Mock AuthContext: provide AuthProvider passthrough and useAuth hook
vi.mock('../context/AuthContext.jsx', () => {
  const AuthContext = React.createContext(null)
  return {
    AuthContext,
    AuthProvider: ({ children }) => children,
    useAuth: () => ({
      user: null,
      users: [],
      login: async () => ({}),
      logout: () => {},
      registerUser: () => {},
      registerGoogleUser: () => {},
      addSubUser: () => {},
      updateSubUser: () => {},
      removeSubUser: () => {},
      getSubUsers: async () => [],
      hasFeatureAccess: () => true,
      getUserFeatures: () => [],
      ALL_FEATURES: []
    })
  }
})

// Mock ThemeContext: provide ThemeProvider passthrough and useTheme hook with full colors
vi.mock('../context/ThemeContext.jsx', () => {
  const ThemeContext = React.createContext(null)
  const colors = {
    primary: '#0284C7', secondary: '#4F46E5', accent: '#9333EA',
    bg1: '#F6F8FA', bg2: '#FFFFFF', bg3: '#EDF2F7', bg4: '#E2E8F0',
    cardBg: 'rgba(255,255,255,0.95)', text1: '#1F2328', text2: '#656D76', border: 'rgba(31,35,40,0.1)',
    success: '#1A7F37', error: '#D1242F'
  }
  return {
    ThemeContext,
    ThemeProvider: ({ children }) => children,
    useTheme: () => ({ isDark: false, mode: 'light', toggleTheme: () => {}, colors }),
  }
})

// Mock Google OAuth hooks used in Signup
vi.mock('@react-oauth/google', () => ({
  useGoogleLogin: (opts) => () => {},
  useGoogleOneTap: () => {},
  GoogleOAuthProvider: ({ children }) => children,
}))

// Mock lucide-react icons to avoid rendering SVG internals in tests
vi.mock('lucide-react', () => {
  const React = require('react')
  return new Proxy({}, {
    get: (_t, prop) => {
      if (prop === '__esModule') return true
      return (props) => React.createElement('span', { 'data-icon': String(prop), ...props }, null)
    }
  })
})
