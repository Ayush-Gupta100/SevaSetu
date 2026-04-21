import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Hexagon, Loader2, Building, User } from 'lucide-react'
import { api } from '../lib/api'

export function Register() {
  const navigate = useNavigate()
  const location = useLocation()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [role, setRole] = useState<'volunteer' | 'ngo'>('volunteer')
  const [addressHint, setAddressHint] = useState('')
  const [formData, setFormData] = useState({ name: '', ngoName: '', registration_number: '', email: '', password: '', address: '' })

  useEffect(() => {
    const params = new URLSearchParams(location.search)
    if (params.get('type') === 'ngo') setRole('ngo')
  }, [location])

  const handleAddressNormalize = async () => {
    if (!formData.address.trim()) {
      return
    }

    try {
      const locationData = await api.geocode({ address: formData.address })
      const normalized = [
        locationData.address,
        locationData.city,
        locationData.state,
        locationData.country,
        locationData.pincode,
      ]
        .filter(Boolean)
        .join(', ')

      if (normalized) {
        setFormData((prev) => ({ ...prev, address: normalized }))
        setAddressHint(`Validated location (ID ${locationData.location_id})`)
      }
    } catch {
      setAddressHint('Unable to validate address right now. Registration will still continue.')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      if (role === 'ngo') {
        // Atomic NGO Registration
        await api.registerNgo({
          admin_name: formData.name,
          admin_email: formData.email,
          admin_password: formData.password,
          ngo_name: formData.ngoName,
          registration_number: formData.registration_number,
          ngo_email: formData.email,
          address: formData.address
        })
      } else {
        // Standard Volunteer Registration
        await api.register({ 
          name: formData.name, 
          email: formData.email, 
          password: formData.password, 
          role: 'volunteer' 
        })
      }

      navigate('/login', { state: { message: 'Account created successfully! Please sign in.' } })
    } catch (err: any) {
      let errorMessage = 'Failed to register. Please try again.'
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
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
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center justify-center">
          <Hexagon className="w-10 h-10 text-primary" />
        </Link>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-foreground">
          Create your account
        </h2>
        <p className="mt-2 text-center text-sm text-muted">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-primary hover:text-primary-hover">
            Sign in
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="glass py-8 px-4 sm:rounded-2xl sm:px-10">
          
          <div className="flex p-1 bg-black/20 rounded-lg mb-6 border border-white/5">
            <button
              type="button"
              className={`flex-1 py-2 text-sm font-medium rounded-md flex items-center justify-center gap-2 transition-colors ${role === 'volunteer' ? 'bg-primary/20 text-primary shadow-sm' : 'text-muted hover:text-white'}`}
              onClick={() => setRole('volunteer')}
            >
              <User className="w-4 h-4" /> Volunteer
            </button>
            <button
              type="button"
              className={`flex-1 py-2 text-sm font-medium rounded-md flex items-center justify-center gap-2 transition-colors ${role === 'ngo' ? 'bg-primary/20 text-primary shadow-sm' : 'text-muted hover:text-white'}`}
              onClick={() => setRole('ngo')}
            >
              <Building className="w-4 h-4" /> NGO
            </button>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg">
                {error}
              </div>
            )}
            {role === 'ngo' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-foreground">NGO Name</label>
                  <input type="text" required onChange={(e) => setFormData({...formData, ngoName: e.target.value})} className="mt-1 appearance-none block w-full px-3 py-2 border border-border rounded-lg shadow-sm placeholder-muted focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-background text-foreground" placeholder="Hope Foundation" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground">Registration Number</label>
                  <input type="text" required onChange={(e) => setFormData({...formData, registration_number: e.target.value})} className="mt-1 appearance-none block w-full px-3 py-2 border border-border rounded-lg shadow-sm placeholder-muted focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-background text-foreground" placeholder="12-3456789" />
                </div>
              </>
            )}
            
            <div>
              <label className="block text-sm font-medium text-foreground">{role === 'ngo' ? 'Admin Full Name' : 'Full Name'}</label>
              <input type="text" required onChange={(e) => setFormData({...formData, name: e.target.value})} className="mt-1 appearance-none block w-full px-3 py-2 border border-border rounded-lg shadow-sm placeholder-muted focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-background text-foreground" placeholder="John Doe" />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground">Email address</label>
              <input type="email" required onChange={(e) => setFormData({...formData, email: e.target.value})} className="mt-1 appearance-none block w-full px-3 py-2 border border-border rounded-lg shadow-sm placeholder-muted focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-background text-foreground" placeholder="you@example.com" />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground">Password</label>
              <input type="password" required onChange={(e) => setFormData({...formData, password: e.target.value})} className="mt-1 appearance-none block w-full px-3 py-2 border border-border rounded-lg shadow-sm placeholder-muted focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-background text-foreground" placeholder="••••••••" />
            </div>

            {role === 'ngo' && (
              <div className="relative">
                <label className="block text-sm font-medium text-foreground">Headquarters Address</label>
                <input
                  type="text"
                  required
                  value={formData.address}
                  onChange={(e) => {
                    setFormData({...formData, address: e.target.value})
                    setAddressHint('')
                  }}
                  onBlur={handleAddressNormalize}
                  className="mt-1 appearance-none block w-full px-3 py-2 border border-border rounded-lg shadow-sm placeholder-muted focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-background text-foreground"
                  placeholder="Street, city, state"
                />
                {addressHint && <p className="mt-1 text-xs text-muted">{addressHint}</p>}
              </div>
            )}

            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 transition-colors"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Create Account'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
