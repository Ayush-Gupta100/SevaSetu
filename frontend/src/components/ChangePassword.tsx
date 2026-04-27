import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, setUserSession } from '../lib/api'
import { useFeedback } from '../lib/feedback'

export function ChangePassword() {
  const navigate = useNavigate()
  const { showSuccess } = useFeedback()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (newPassword !== confirmPassword) {
      setError('New password and confirmation do not match.')
      return
    }

    setLoading(true)
    try {
      await api.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      })

      // Refresh profile after password update so role-based redirect is always accurate.
      const profile = await api.getProfile()
      setUserSession(profile)

      if (profile.must_change_password) {
        setError('Password update did not complete. Please try again.')
        return
      }

      showSuccess('Password updated successfully. Please continue to your dashboard.')
      if (profile.role === 'ngo_admin') {
        navigate('/dashboard')
      } else {
        navigate('/member-dashboard')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to change password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto py-8">
      <div className="glass rounded-2xl p-6">
        <h1 className="text-2xl font-bold text-foreground/90">Change Password</h1>
        <p className="text-sm text-muted mt-1">For security, please change your temporary password before continuing.</p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          {error && <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">{error}</div>}

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Current Password</label>
            <input
              type="password"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">New Password</label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Confirm New Password</label>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-lg bg-primary text-white font-medium hover:bg-primary-hover transition-colors disabled:opacity-50"
          >
            {loading ? 'Updating...' : 'Update Password'}
          </button>
        </form>
      </div>
    </div>
  )
}
