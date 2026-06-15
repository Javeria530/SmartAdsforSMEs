import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

import LoginPage from '../views/LoginPage.jsx'
import SignupPage from '../views/SignupPage.jsx'
import { AuthProvider } from '../context/AuthContext.jsx'
import { ThemeProvider } from '../context/ThemeContext.jsx'

describe('Auth pages render', () => {
  test('Login page has email and password inputs', () => {
    render(
      <AuthProvider>
        <ThemeProvider>
          <LoginPage />
        </ThemeProvider>
      </AuthProvider>
    )
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })

  test('Signup page has required fields', () => {
    render(
      <AuthProvider>
        <ThemeProvider>
          <SignupPage />
        </ThemeProvider>
      </AuthProvider>
    )
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
  })
})
