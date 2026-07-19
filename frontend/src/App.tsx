// src/App.tsx
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/components/ThemeProvider'
import { Layout } from '@/components/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'
import { Profile } from '@/pages/Profile'
import { Settings } from '@/pages/Settings'
import { Reports } from '@/pages/Reports'
import { Transactions } from '@/pages/Transactions'
import { Investments } from '@/pages/Investments'
import { Borrow } from '@/pages/Borrow'
import { Transfers } from '@/pages/Transfers'
import { CreditCards } from '@/pages/CreditCards'
import { Savings } from '@/pages/Savings'
import { useAuth } from '@/hooks/useAuth'
import { Toaster } from 'sonner'

const queryClient = new QueryClient()

function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="dark" storageKey="izhar-theme">
        <Router>
          <Toaster richColors position="top-right" />
          {!user ? (
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="*" element={<Navigate to="/login" />} />
            </Routes>
          ) : (
            <Layout>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/transactions" element={<Transactions />} />
                <Route path="/investments" element={<Investments />} />
                <Route path="/borrow" element={<Borrow />} />
                <Route path="/transfers" element={<Transfers />} />
                <Route path="/credit-cards" element={<CreditCards />} />
                <Route path="/savings" element={<Savings />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="*" element={<Navigate to="/dashboard" />} />
              </Routes>
            </Layout>
          )}
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  )
}
