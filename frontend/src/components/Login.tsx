import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Hexagon, Loader2 } from 'lucide-react'
import { api, clearAuthStorage, setUserSession } from '../lib/api'
import { ThemeToggle } from './ThemeToggle'

export function Login() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [forgotPassword, setForgotPassword] = useState(false)
  const [resetSent, setResetSent] = useState(false)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (forgotPassword) {
      setLoading(true)
      setTimeout(() => {
        setLoading(false)
        setResetSent(true)
      }, 1000)
      return
    }

    setLoading(true)
    setError('')
    try {
      clearAuthStorage()

      // 1. Get Token
      const res = await api.login({ email, password })
      const token = res.access_token || res.token
      const mustChangePassword = Boolean(res.must_change_password)
      if (!token) {
        throw new Error('Login response missing access token.')
      }

      // Save token first so authenticated calls include Authorization header.
      setUserSession({}, token)

      // 2. Fetch Profile to get role and ngo_id
      const profile = await api.getProfile()
      const role = profile.role
      setUserSession(profile, token)

      if (mustChangePassword || profile.must_change_password) {
        navigate('/change-password')
        return
      }
      
      // 3. Redirect
      if (role === 'ngo_admin') {
        navigate('/dashboard')
      } else if (role === 'ngo_member' || role === 'volunteer') {
        navigate('/member-dashboard')
      } else {
        navigate('/member-dashboard')
      }
    } catch (err: any) {
      let errorMessage = 'Failed to login. Please check credentials.'
      const detail = err.response?.data?.detail
      if (err.response?.status === 401) {
        errorMessage = 'Invalid credentials. If you are trying to create an account, please click "Register here" below.'
      } else if (Array.isArray(detail)) {
        errorMessage = detail.map((d: any) => `${d.loc[d.loc.length - 1]}: ${d.msg}`).join(', ')
      } else if (typeof detail === 'string') {
        errorMessage = detail
      } else if (err.message) {
        errorMessage = err.message
      }
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-surface">
      <div className="absolute top-4 right-4">
        <ThemeToggle className="px-2.5 py-1.5 text-xs shadow-none" />
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center justify-center">
          <Hexagon className="w-10 h-10 text-primary" />
        </Link>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-foreground">
          {forgotPassword ? 'Reset Password' : 'Welcome back'}
        </h2>
        <p className="mt-2 text-center text-sm text-muted">
          {forgotPassword ? 'Enter your email to receive a reset link' : 'Don\'t have an account?'} {' '}
          {!forgotPassword && (
            <Link to="/register" className="font-medium text-primary hover:text-primary-hover">
              Register here
            </Link>
          )}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-background py-8 px-4 shadow-sm border border-border/50 sm:rounded-2xl sm:px-10">
          {resetSent ? (
            <div className="text-center">
              <div className="p-4 bg-green-50 text-green-700 text-sm rounded-lg mb-4">
                If an account exists for {email}, a password reset link has been sent.
              </div>
              <button onClick={() => {setForgotPassword(false); setResetSent(false)}} className="font-medium text-primary hover:text-primary-hover">
                Return to Login
              </button>
            </div>
          ) : (
            <form className="space-y-6" onSubmit={handleSubmit}>
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg">
                  {error}
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-foreground">Email address</label>
                <div className="mt-1">
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="appearance-none block w-full px-3 py-2 border border-border rounded-lg shadow-sm placeholder-muted focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-white"
                    placeholder="you@example.com"
                  />
                </div>
              </div>

              {!forgotPassword && (
                <div>
                  <label className="block text-sm font-medium text-foreground">Password</label>
                  <div className="mt-1">
                    <input
                      type="password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="appearance-none block w-full px-3 py-2 border border-border rounded-lg shadow-sm placeholder-muted focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-white"
                      placeholder="••••••••"
                    />
                  </div>
                </div>
              )}

              {!forgotPassword && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      className="h-4 w-4 text-primary focus:ring-primary border-border rounded"
                    />
                    <label className="ml-2 block text-sm text-muted">Remember me</label>
                  </div>
                  <div className="text-sm">
                    <button type="button" onClick={() => setForgotPassword(true)} className="font-medium text-primary hover:text-primary-hover">
                      Forgot password?
                    </button>
                  </div>
                </div>
              )}

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 transition-colors"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (forgotPassword ? 'Send Reset Link' : 'Sign In')}
                </button>
              </div>

              {forgotPassword && (
                <div className="text-center">
                  <button type="button" onClick={() => setForgotPassword(false)} className="text-sm text-muted hover:text-primary transition-colors">
                    Back to Sign In
                  </button>
                </div>
              )}
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
