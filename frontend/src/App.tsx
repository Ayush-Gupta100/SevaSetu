import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { Header } from './components/Header'
import { Dashboard } from './components/Dashboard'
import { Problems } from './components/Problems'
import { Tasks } from './components/Tasks'
import { Inventory } from './components/Inventory'
import { Finance } from './components/Finance'
import { Insights } from './components/Insights'
import { Landing } from './components/Landing'
import { Login } from './components/Login'
import { Register } from './components/Register'
import { Notifications } from './components/Notifications'
import { DataImport } from './components/Import'
import { Team } from './components/Team'
import { MemberDashboard } from './components/MemberDashboard'
import { ChangePassword } from './components/ChangePassword'
import { getAuthToken, getUserRole } from './lib/api'
import { FeedbackProvider } from './lib/feedback'
import { ThemeProvider } from './lib/theme'

function ProtectedRoute({ allowedRoles }: { allowedRoles?: string[] }) {
  const token = getAuthToken()
  const role = getUserRole()

  if (!token) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && (!role || !allowedRoles.includes(role))) {
    return <Navigate to="/tasks" replace />
  }

  return <Outlet />
}

function PublicOnlyRoute() {
  const token = getAuthToken()
  const role = getUserRole()
  if (token) {
    if (role === 'ngo_admin') {
      return <Navigate to="/dashboard" replace />
    }
    return <Navigate to="/member-dashboard" replace />
  }
  return <Outlet />
}

function AppLayout() {
  return (
    <div className="flex h-screen bg-background overflow-hidden selection:bg-primary/30">
      <Sidebar />
      <div className="flex flex-col flex-1 relative">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 scrollbar-hide">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

function App() {
  return (
    <ThemeProvider>
      <FeedbackProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Landing />} />

            <Route element={<PublicOnlyRoute />}>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Route>

            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/change-password" element={<ChangePassword />} />
                <Route path="/member-dashboard" element={<MemberDashboard />} />
                <Route path="/problems" element={<Problems />} />
                <Route path="/tasks" element={<Tasks />} />
                <Route path="/notifications" element={<Notifications />} />
              </Route>
            </Route>

            <Route element={<ProtectedRoute allowedRoles={['ngo_admin', 'ngo_member']} />}>
              <Route element={<AppLayout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/inventory" element={<Inventory />} />
                <Route path="/finance" element={<Finance />} />
                <Route path="/insights" element={<Insights />} />
                <Route path="/import" element={<DataImport />} />
                <Route path="/team" element={<Team />} />
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </FeedbackProvider>
    </ThemeProvider>
  )
}

export default App
