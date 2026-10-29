import {
  StrictMode,
} from 'react'

import {
  createRoot,
} from 'react-dom/client'

import {
  BrowserRouter,
} from 'react-router-dom'

import {
  QueryClientProvider,
} from '@tanstack/react-query'

import App from './App'

import AuthProvider from
  './auth/AuthProvider'

import {
  queryClient,
} from './app/queryClient'

import './index.css'
import './styles/base.css'
import './styles/layout.css'
import './styles/dashboard.css'
import './styles/students.css'

createRoot(
  document.getElementById(
    'root',
  )!,
).render(
  <StrictMode>
    <QueryClientProvider
      client={queryClient}
    >
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)