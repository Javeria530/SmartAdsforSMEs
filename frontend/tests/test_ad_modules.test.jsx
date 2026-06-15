import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

import VideoAdModule from '../components/Dashboard/VideoAdModule.jsx'
import VideoAdModuleOld from '../components/Dashboard/VideoAdModule.jsx'
import Dashboard from '../views/Dashboard.jsx'
import { AuthProvider } from '../context/AuthContext.jsx'
import { ThemeProvider } from '../context/ThemeContext.jsx'

describe('Ad modules render', () => {
  test('VideoAdModule renders basic controls', () => {
    render(
      <AuthProvider>
        <ThemeProvider>
          <VideoAdModule />
        </ThemeProvider>
      </AuthProvider>
    )
    // Assert for a button or heading commonly present in module
    const maybeButton = screen.queryByRole('button')
    expect(maybeButton).toBeInTheDocument()
  })

  test('Dashboard contains Type radio options for ad type', () => {
    render(
      <AuthProvider>
        <ThemeProvider>
          <Dashboard />
        </ThemeProvider>
      </AuthProvider>
    )
    expect(screen.getByText(/Type:/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Logo/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Poster/i)).toBeInTheDocument()
  })
})
