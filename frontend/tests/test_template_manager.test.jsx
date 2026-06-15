import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

import TemplateManager from '../components/TemplateManager/TemplateManager.jsx'
import { AuthProvider } from '../context/AuthContext.jsx'
import { ThemeProvider } from '../context/ThemeContext.jsx'

describe('TemplateManager component', () => {
  test('renders header and fixed templates', () => {
    render(
      <AuthProvider>
        <ThemeProvider>
          <TemplateManager onBack={() => {}} />
        </ThemeProvider>
      </AuthProvider>
    )

    // Header
    expect(screen.getByText(/Template Manager/i)).toBeInTheDocument()

    // Fixed templates from the component should be rendered
    expect(screen.getByText(/Elite Tech AI Branding/i)).toBeInTheDocument()
    expect(screen.getByText(/Signature Burger Reveal/i)).toBeInTheDocument()
  })
})
